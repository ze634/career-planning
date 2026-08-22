# -*- coding: utf-8 -*-
"""build_pdf.py <plan.md> <output.pdf> — Markdown → HTML → PDF（自包含，仅用标准库 + Node/Playwright）

用法:
    python build_pdf.py plan.md 职业规划.pdf
    python build_pdf.py plan.md 职业规划.pdf --keep-html   # 保留中间 HTML（默认保留在 PDF 同目录）

依赖: Python 3 + Node.js + Playwright（Chromium）。
定位策略: 环境变量 NODE / PLAYWRIGHT_REQUIRE 优先，其次常见本机路径，最后 PATH。
"""
import io
import os
import re
import shutil
import subprocess
import sys

# ---------- Markdown → HTML（最小转换器，支持 1-6 级标题/列表/表格/粗体/行内代码/引用/分隔线） ----------
def inline(s):
    s = re.sub(r'`([^`]+)`', r'<code>\1</code>', s)
    s = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', s)
    s = re.sub(r'(?<!\*)\*([^*]+)\*(?!\*)', r'<em>\1</em>', s)
    return s

def md_to_html(md_text):
    lines = md_text.split('\n')
    out, i, n = [], 0, len(lines)
    head = re.compile(r'^(#{1,6})\s+(.*)$')

    def flush(buf):
        if buf:
            out.append('<p>' + inline(' '.join(buf)) + '</p>')
            buf.clear()

    while i < n:
        line = lines[i]
        if not line.strip():
            i += 1
            continue
        m = head.match(line)
        if m:
            lvl = len(m.group(1))
            out.append('<h%d>%s</h%d>' % (lvl, inline(m.group(2)), lvl))
            i += 1
            continue
        if line.strip() == '---':
            out.append('<hr>')
            i += 1
            continue
        if line.startswith('> '):
            buf = []
            while i < n and lines[i].startswith('> '):
                buf.append(lines[i][2:])
                i += 1
            out.append('<blockquote>' + inline(' '.join(buf)) + '</blockquote>')
            continue
        if line.startswith('|') and i + 1 < n and re.match(r'^\|[\s:\-|]+\|?$', lines[i + 1]):
            def cells(r):
                r = r.strip()
                if r.startswith('|'): r = r[1:]
                if r.endswith('|'): r = r[:-1]
                return [c.strip() for c in r.split('|')]
            header = cells(lines[i])
            i += 2
            rows = []
            while i < n and lines[i].strip().startswith('|'):
                rows.append(cells(lines[i]))
                i += 1
            out.append('<table><thead><tr>' + ''.join('<th>' + inline(c) + '</th>' for c in header) + '</tr></thead><tbody>')
            for r in rows:
                out.append('<tr>' + ''.join('<td>' + inline(c) + '</td>' for c in r) + '</tr>')
            out.append('</tbody></table>')
            continue
        if line.startswith('- '):
            buf = []
            while i < n and lines[i].startswith('- '):
                buf.append(inline(lines[i][2:]))
                i += 1
            out.append('<ul>' + ''.join('<li>' + b + '</li>' for b in buf) + '</ul>')
            continue
        if re.match(r'^\d+\.\s', line):
            buf = []
            while i < n and re.match(r'^\d+\.\s', lines[i]):
                buf.append(inline(re.sub(r'^\d+\.\s', '', lines[i])))
                i += 1
            out.append('<ol>' + ''.join('<li>' + b + '</li>' for b in buf) + '</ol>')
            continue
        buf = []
        while i < n and lines[i].strip() and not lines[i].startswith(('#', '|', '- ', '> ')) and not re.match(r'^\d+\.\s', lines[i]):
            buf.append(lines[i].strip())
            i += 1
        flush(buf)
        if not buf:
            i += 1
    return '\n'.join(out)

CSS = '''
  @page { size: A4; margin: 16mm 15mm; }
  * { box-sizing: border-box; }
  body { font-family: 'Microsoft YaHei','PingFang SC','Noto Sans CJK SC',sans-serif; font-size: 10.5pt; line-height: 1.65; color: #1a1a2e; margin: 0; }
  h1 { font-size: 19pt; text-align: center; margin: 0 0 4pt; color: #0f3d5c; }
  h2 { font-size: 14pt; margin: 14pt 0 6pt; padding-bottom: 3pt; border-bottom: 2px solid #187aa6; color: #0f3d5c; page-break-after: avoid; }
  h3 { font-size: 12pt; margin: 10pt 0 4pt; color: #187aa6; page-break-after: avoid; }
  h4 { font-size: 11pt; margin: 8pt 0 3pt; color: #33475b; page-break-after: avoid; }
  p { margin: 4pt 0; }
  ul, ol { margin: 4pt 0 4pt 2pt; padding-left: 18pt; }
  li { margin: 2pt 0; }
  table { border-collapse: collapse; width: 100%; margin: 6pt 0; font-size: 9.5pt; }
  th, td { border: 1px solid #b8c4cc; padding: 4pt 6pt; text-align: left; vertical-align: top; }
  th { background: #e8f1f6; color: #0f3d5c; font-weight: bold; }
  tr { page-break-inside: avoid; }
  blockquote { margin: 6pt 0; padding: 6pt 10pt; background: #f4f8fa; border-left: 3px solid #187aa6; color: #33475b; }
  code { background: #eef2f5; padding: 0 3px; border-radius: 3px; font-family: Consolas, monospace; font-size: 9.5pt; }
  hr { border: none; border-top: 1px solid #c5d2da; margin: 10pt 0; }
  strong { color: #0f3d5c; }
'''

def find_node():
    cands = [os.environ.get('NODE'),
             r'C:\Users\灵泽\.ai-manager\runtimes\node\24.18.1\node.exe',
             r'C:\Users\灵泽\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe']
    for c in cands:
        if c and os.path.exists(c):
            return c
    return shutil.which('node')

def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    md_path = sys.argv[1]
    pdf_path = sys.argv[2]
    keep_html = '--keep-html' in sys.argv
    md_text = io.open(md_path, encoding='utf-8').read()
    html_path = os.path.splitext(pdf_path)[0] + '.html'
    html = '<!DOCTYPE html><html lang="zh-CN"><head><meta charset="UTF-8"><title>职业规划</title><style>' + CSS + '</style></head><body>\n' + md_to_html(md_text) + '\n</body></html>'
    io.open(html_path, 'w', encoding='utf-8', newline='').write(html)
    node = find_node()
    if not node:
        print('未找到 Node.js：设置环境变量 NODE 指向 node 可执行文件，或将其加入 PATH。')
        sys.exit(2)
    script = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'render-pdf.js')
    r = subprocess.run([node, script, html_path, pdf_path])
    if r.returncode != 0:
        print('PDF 渲染失败，中间 HTML 保留在: ' + html_path)
        sys.exit(r.returncode)
    if not keep_html and os.path.exists(html_path):
        os.remove(html_path)
    print('完成: ' + pdf_path)

if __name__ == '__main__':
    main()
