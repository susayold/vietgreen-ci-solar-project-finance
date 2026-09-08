from pathlib import Path

p = Path('app/economics/economics.css')
text = p.read_text(encoding='utf-8')
marker = '/* Final content-audit responsive guards. */'
if marker not in text:
    text += '''\n\n/* Final content-audit responsive guards. */\n.economics-page .currency-panel span,\n.economics-page .currency-panel b,\n.economics-page .portfolio-status span,\n.economics-page .decision-ladder strong,\n.economics-page .commercial-status > strong {\n  min-width: 0;\n  overflow-wrap: anywhere;\n  word-break: break-word;\n}\n.economics-page .currency-panel span {\n  gap: 10px;\n}\n@media (max-width: 760px) {\n  .economics-page .portfolio-status {\n    grid-template-columns: 1fr;\n  }\n  .economics-page .currency-panel span {\n    align-items: flex-start;\n    flex-wrap: wrap;\n  }\n}\n'''
    p.write_text(text, encoding='utf-8')
