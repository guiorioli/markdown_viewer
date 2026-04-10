#!/usr/bin/env bash
set -e

echo "Instalando dependencias..."
python -m pip install pyinstaller markdown2 tkinterweb

echo ""
echo "Compilando Markdown Viewer..."
python -m PyInstaller --onedir --windowed --name markdown_viewer main.py

echo ""
echo "Limpando arquivos temporarios..."
rm -rf build markdown_viewer.spec

echo ""
echo "Renomeando executavel..."
mv dist/markdown_viewer/markdown_viewer dist/markdown_viewer/md

echo ""
echo "Pronto! Executavel gerado em: dist/markdown_viewer/md"
