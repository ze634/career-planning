// render-pdf.js <input.html> <output.pdf> — HTML→PDF via Playwright (Chromium headless)
// 自包含：从多个常见位置解析 playwright；找不到时给出安装指引。
const fs = require('fs');
const path = require('path');

function findPlaywright() {
  const candidates = [
    process.env.PLAYWRIGHT_REQUIRE,
    'F:/DNM/bi/career-ops/node_modules/playwright',
    'C:/Users/灵泽/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright',
  ].filter(Boolean);
  for (const c of candidates) {
    try { require.resolve(c); return c; } catch (e) {}
  }
  // 脚本所在目录向上逐级找 node_modules/playwright（skill 被放进某个项目时可用）
  let dir = __dirname;
  while (true) {
    const p = path.join(dir, 'node_modules', 'playwright');
    if (fs.existsSync(p)) return p;
    const parent = path.dirname(dir);
    if (parent === dir) break;
    dir = parent;
  }
  return null;
}

(async () => {
  const [inputHtml, outputPdf] = process.argv.slice(2);
  if (!inputHtml || !outputPdf) {
    console.error('用法: node render-pdf.js <input.html> <output.pdf>');
    process.exit(1);
  }
  const pw = findPlaywright();
  if (!pw) {
    console.error('未找到 playwright。安装后重试：npm i playwright && npx playwright install chromium，或用 PLAYWRIGHT_REQUIRE 指定模块路径。');
    process.exit(2);
  }
  const { chromium } = require(pw);
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.goto('file:///' + path.resolve(inputHtml).replace(/\\/g, '/'));
  await page.pdf({
    path: path.resolve(outputPdf),
    format: 'A4',
    printBackground: true,
    margin: { top: '0', right: '0', bottom: '0', left: '0' },
  });
  await browser.close();
  console.log('PDF OK: ' + outputPdf);
})().catch((e) => { console.error(e); process.exit(1); });
