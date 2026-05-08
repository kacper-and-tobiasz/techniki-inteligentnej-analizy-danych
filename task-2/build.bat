@echo off

uv add --dev pyinstaller
uv sync
uv run pyinstaller ^
    --windowed ^
    --onedir ^
    --noconfirm ^
    --name "FiltrPrzepisow" ^
    --add-data "data/recipes.json;data" ^
    --collect-data "whisper" ^
    main.py

pause
