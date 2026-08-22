# career-planning 职业规划 Skill

基于简历、个人约束问答与宏观环境（中国五年规划、康波周期等经济周期），生成多年（默认十年）职业规划 PDF 的 Codex skill。

## 工作流
1. **输入**：读取简历（markdown/txt/PDF/HTML），并向用户提问约束条件（年限、目标方向、城市与异地意愿、收入家庭预期、风险偏好、学历提升等）
2. **能力定位合成**：把简历经历/技能合成为差异化定位 + SWOT（不虚构量化数据）
3. **宏观研究**：联网优先（搜索最新五年规划/经济周期/行业趋势并标注来源日期）；离线兜底用 `references/macro-environment.md`
4. **撰写规划**：按 `references/plan-template.md` 结构生成 `plan.md`（年限/城市/方向参数化）
5. **渲染 PDF**：`python scripts/build_pdf.py plan.md 职业规划.pdf`（自包含 md→HTML→PDF）

## 目录结构
```
career-planning/
├── SKILL.md                      技能入口与工作流
├── agents/openai.yaml            UI 元数据
├── scripts/
│   ├── build_pdf.py              md → PDF（自动定位 Node/Playwright）
│   └── render-pdf.js             HTML → PDF（Playwright）
└── references/
    ├── plan-template.md          规划结构规范
    └── macro-environment.md      内置宏观环境参考（数据截至 2026-08）
```

## 依赖
- Python 3（标准库）
- Node.js + Playwright（Chromium）：`npm i playwright && npx playwright install chromium`，或设置 `NODE` / `PLAYWRIGHT_REQUIRE` 环境变量指向本机路径

## 硬性规则
- 先提问后规划；规划必须反映用户约束
- 康波周期/经济周期 = 参考框架，非确定性预测，必须标注来源与不确定性
- 量化数据只允许来自简历真实记录或标注"预估"的推算

## 安装
把本目录复制到 `~/.codex/skills/career-planning` 即可被 Codex 识别。

## License
MIT
