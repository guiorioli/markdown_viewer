#!/usr/bin/env bash
set -e

echo "Compilando Markdown Viewer..."
python -m PyInstaller --onedir --windowed --name markdown_viewer main.py

echo ""
echo "Limpando arquivos temporarios..."
rm -rf build markdown_viewer.spec

echo ""
echo "Pronto! Executavel gerado em: dist/markdown_viewer/markdown_viewer"
