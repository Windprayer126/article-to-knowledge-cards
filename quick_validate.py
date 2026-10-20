#!/usr/bin/env python3
"""quick_validate.py — 最小结构验证器，用于验证 skills/ 下的 Skill 是否符合开源发布标准。

检查项：
  1. SKILL.md 存在且 frontmatter 可解析，name / description 非空
  2. name 符合 ^[a-z0-9-]{1,64}$，且与技能目录名一致
  3. description 非空且不超过 1024 字符
  4. agents/openai.yaml 存在，name 与 SKILL.md 一致，含 description 与 instructions
  5. 不包含超出声明范围的产物（当前版本只允许 SKILL.md、agents/openai.yaml、assets/）
  6. 图标 assets/icon.png 存在

用法：
  python3 quick_validate.py [skill_path]
  缺省 skill_path = <脚本所在目录>/skills/ielts-corpus-builder

退出码：0 = 全部通过；1 = 存在失败项。
"""

import re
import sys
from pathlib import Path

NAME_RE = re.compile(r"^[a-z0-9-]{1,64}$")
MAX_DESC_LEN = 1024

ALLOWED_TOP = {"SKILL.md", "agents", "assets"}
ALLOWED_AGENTS = {"openai.yaml"}


def fail_prefix():
    return "\033[31mFAIL\033[0m"


def ok_prefix():
    return "\033[32mPASS\033[0m"


def parse_simple_frontmatter(text):
    """解析 SKILL.md 顶部 --- 包裹的 frontmatter（支持单行 key: value）。"""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None, "SKILL.md 缺少 frontmatter（首行必须是 ---）"
    try:
        end = lines.index("---", 1)
    except ValueError:
        return None, "frontmatter 未正确闭合（缺少第二个 ---）"
    fm = {}
    for line in lines[1:end]:
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if ":" in line and not line.startswith((" ", "\t")):
            key, _, value = line.partition(":")
            fm[key.strip()] = value.strip().strip('"').strip("'")
    return fm, None


def parse_openai_yaml(path):
    """解析 agents/openai.yaml：优先 PyYAML，缺失时退化为顶层 key 检查。"""
    text = path.read_text(encoding="utf-8")
    try:
        import yaml  # type: ignore

        data = yaml.safe_load(text)
        return (data if isinstance(data, dict) else {}), None
    except ImportError:
        data = {}
        for line in text.splitlines():
            if re.match(r"^[A-Za-z_-]+:", line):
                key, _, raw = line.partition(":")
                value = raw.strip().strip('"').strip("'")
                # 顶层单行键保留真实值；块标量键（值为空，如 description: >）标记为存在
                data[key.strip()] = value if value else "present"
        return data, None
    except Exception as exc:  # YAML 语法错误
        return {}, f"YAML 解析失败：{exc}"


def main():
    base = Path(__file__).resolve().parent
    skill_path = Path(sys.argv[1]) if len(sys.argv) > 1 else base / "skills" / "ielts-corpus-builder"
    skill_path = skill_path.resolve()

    results = []

    def check(name, passed, detail=""):
        results.append((name, passed, detail))
        print(f"[{ok_prefix() if passed else fail_prefix()}] {name}" + (f" — {detail}" if detail else ""))

    print(f"验证目标：{skill_path}\n")

    # 1-3. SKILL.md 与 frontmatter
    skill_md = skill_path / "SKILL.md"
    if not skill_md.is_file():
        check("SKILL.md 存在", False, f"未找到 {skill_md}")
        print("\n存在失败项，验证未通过。")
        sys.exit(1)
    check("SKILL.md 存在", True)

    fm, err = parse_simple_frontmatter(skill_md.read_text(encoding="utf-8"))
    check("frontmatter 可解析", err is None, err or "")
    if fm is None:
        print("\n存在失败项，验证未通过。")
        sys.exit(1)

    name = fm.get("name", "")
    check("name 非空", bool(name))
    check("name 格式合法 ^[a-z0-9-]{1,64}$", bool(NAME_RE.match(name)), name)
    check("name 与目录名一致", name == skill_path.name, f"name={name!r} dir={skill_path.name!r}")

    desc = fm.get("description", "")
    check("description 非空", bool(desc))
    check(f"description ≤ {MAX_DESC_LEN} 字符", len(desc) <= MAX_DESC_LEN, f"当前 {len(desc)} 字符")

    # 4. agents/openai.yaml
    openai_yaml = skill_path / "agents" / "openai.yaml"
    if openai_yaml.is_file():
        check("agents/openai.yaml 存在", True)
        data, err = parse_openai_yaml(openai_yaml)
        check("openai.yaml 可解析", err is None, err or "")
        if not err:
            yaml_name = str(data.get("name", ""))
            check("openai.yaml name 与 SKILL.md 一致", yaml_name == name, f"openai.yaml name={yaml_name!r}")
            check("openai.yaml 含 description", bool(data.get("description")))
            check("openai.yaml 含 instructions", bool(data.get("instructions")))
    else:
        check("agents/openai.yaml 存在", False, "开源多平台适配需要该文件")

    # 5. 产物范围（当前声明：纯文本处理技能，无脚本依赖）
    top_entries = {p.name for p in skill_path.iterdir()}
    unexpected_top = top_entries - ALLOWED_TOP
    check(
        "顶层产物符合声明范围（SKILL.md / agents / assets）",
        not unexpected_top,
        f"多余项：{sorted(unexpected_top)}" if unexpected_top else "",
    )
    agents_dir = skill_path / "agents"
    if agents_dir.is_dir():
        unexpected_agents = {p.name for p in agents_dir.iterdir()} - ALLOWED_AGENTS
        check("agents/ 仅含 openai.yaml", not unexpected_agents,
              f"多余项：{sorted(unexpected_agents)}" if unexpected_agents else "")

    # 6. 图标
    icon = skill_path / "assets" / "icon.png"
    check("assets/icon.png 存在", icon.is_file())

    # 汇总
    failed = [r for r in results if not r[1]]
    print(f"\n共 {len(results)} 项检查，通过 {len(results) - len(failed)}，失败 {len(failed)}。")
    if failed:
        print("失败项：")
        for n, _, d in failed:
            print(f"  - {n}" + (f"（{d}）" if d else ""))
        sys.exit(1)
    print("✅ 全部通过。")


if __name__ == "__main__":
    main()
