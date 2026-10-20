# ielts-corpus-builder

雅思外刊精读语料库构建器：把一篇英文外刊文章变成三张雅思 8 分水平的备考卡片，可直接粘贴进 Notability 等笔记应用。

## 它做什么

粘贴英文外刊文章（社论 / 评论 / 报道），得到一份精读报告，包含三个模块：

| 模块 | 内容 | 限额 |
|---|---|---|
| 一、黄金功能句 | 功能标签 + 原句摘抄 + 入选理由 + 话题仿写（含"安全化改装"） | ≤ 3 句 |
| 二、核心词汇链 | 📘 写作专用 / 🗣️ 口语专用 / ⚖️ 专业领域词，每词含【词性+中文意义】【入选理由】【雅思迁移句】 | 4-7 个 |
| 三、精读指导与避坑指南 | 中文一句话核心立场与论证走向 + 词汇/句式/逻辑三维难度对比 + 避坑提示 | — |

设计原则：

- 只提取有迁移价值的**逻辑骨架**（如 `It's not that... It's that...`、`Even if you..., you should...`），不挑华丽辞藻。
- **安全化改装**：仿写时替换生僻词、剔除过度政治化表述、拆短易错从句，语法宁简勿错。
- **宁缺毋滥**：纯新闻短讯信息不足时宁可少提取，绝不凑数；零编造，摘抄逐字来自原文。

## 使用方法

1. 在对话中直接粘贴英文文章的纯文本 / Markdown（一次一篇）。
2. 说一句"帮我做精读"或"提取雅思语料"即可。
3. 拿到报告后，按模块直接复制粘贴到笔记应用复习。

**暂不支持**：网页抓取 / URL、PDF / 图片文件、Anki 导出、图形界面。

## 输入示例（节选）

> The problem is not that green technology is too expensive; it is that fossil fuels remain too cheap. ... Critics warn that carbon taxes would cripple growth and punish the poor. The evidence suggests otherwise — and where the burden does bite, the answer is to recycle the revenue as dividends, not to abandon the instrument altogether.

## 输出示例（节选）

### 1️⃣ 【功能标签】#否定重构
> 【原句摘抄】The problem is not that green technology is too expensive; it is that fossil fuels remain too cheap.

【入选理由】"not that A; it is that B" 先否定流行误解、再抛出真因，是 Task 2 驳论段最能体现论证层次的高分骨架。
【仿写示范】The problem is not that students spend too much time online; it is that schools fail to teach them how to use it productively.（话题迁移到教育）

完整输入输出示例见 `tests/inputs/` 与 `tests/outputs/`。

## 项目结构

```
skills/ielts-corpus-builder/
├── SKILL.md            # 技能主指令（三模块格式与红线清单）
├── agents/openai.yaml  # OpenAI 平台适配元数据
└── assets/icon.png     # 技能图标
tests/
├── inputs/             # 测试夹具：环境社论、法律报道
└── outputs/            # 测试产出的两份精读报告
quick_validate.py       # 结构验证脚本
```

运行验证：

```bash
python3 quick_validate.py
```

## License

MIT（完整文本见根目录 [LICENSE](LICENSE)）
