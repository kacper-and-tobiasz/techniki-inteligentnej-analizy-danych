@echo off

pyinstaller ^
    --noconfirm ^
    --onedir ^
    --windowed ^
    --name "FiltrPrzepisow" ^
    --add-data "data/recipes.json;data" ^
    --hidden-import "whisper" ^
    --hidden-import "sounddevice" ^
    --hidden-import "scipy.io.wavfile" ^
    --hidden-import "numpy" ^
    --hidden-import "PySide6" ^
    --collect-data "whisper" ^
    --collect-all "imageio_ffmpeg" ^
    main.py

pause
