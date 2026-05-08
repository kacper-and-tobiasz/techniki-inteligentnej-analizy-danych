@echo off

pip install pyinstaller

pyinstaller ^
    --windowed ^
    --onedir ^
    --noconfirm ^
    --name "FiltrPrzepisow" ^
    --add-data "data/recipes.json;data" ^
    --collect-data "whisper" ^
    main.py

pause
