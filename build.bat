@echo off
echo Compilando Markdown Viewer...
python -m PyInstaller --onedir --windowed --name markdown_viewer main.py

echo.
echo Limpando arquivos temporarios...
if exist build rmdir /s /q build
if exist markdown_viewer.spec del /q markdown_viewer.spec

echo.
echo Pronto! Executavel gerado em: dist\markdown_viewer\markdown_viewer.exe
pause
