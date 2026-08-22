## 依赖
- Python 3（标准库）
- Node.js，并在 **skill 目录内**安装 Playwright（渲染 PDF 用）：

```bash
cd ~/.codex/skills/career-planning
npm i playwright
npx playwright install chromium
```

- 也可以把已安装的 playwright 模块路径设到环境变量 `PLAYWRIGHT_REQUIRE`（如 `C:\...\node_modules\playwright`）；Node 可执行文件路径可用环境变量 `NODE` 指定或直接加入 PATH
