// render-pdf.js <input.html> <output.pdf> — HTML→PDF via Playwright (Chromium headless)
// 跨机器可用：优先标准 require('playwright')（随项目/全局安装），其次 PLAYWRIGHT_REQUIRE，
// 再次向上级目录找 node_modules/playwright，最后兜底作者机器的已知路径。
const fs = require('fs');
const path = require('path');

function findPlaywright() {
  // 1) 标准 Node 模块解析：skill 所在项目装了 playwright 或设置了 NODE_PATH 即可命中
  try { require.resolve('playwright'); return 'playwright'; } catch (e) {}
  // 2) 显式指定
  if (process.env.PLAYWRIGHT_REQUIRE) {
    try { require.resolve(process.env.PLAYWRIGHT_REQUIRE); return process.env.PLAYWRIGHT_REQUIRE; } catch (e) {}
  }
  // 3) 向上逐级找 node_modules/playwright
  let dir = __dirname;
  while (true) {
    const p = path.join(dir, 'node_modules', 'playwright');
    if (fs.existsSync(p)) return p;
    const parent = path.dirname(dir);
    if (parent === dir) break;
    dir = parent;
  }
  // 4) 兜底：PLAYWRIGHT_REQUIRE 已在步骤 2 处理；此处不再内置任何机器路径
  for (const c of [
  ]) {
    try { require.resolve(c); return c; } catch (e) {}
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
    console.error('未找到 playwright。在 skill 所在项目执行：npm i playwright && npx playwright install chromium；或用 PLAYWRIGHT_REQUIRE 指定模块路径。');
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
