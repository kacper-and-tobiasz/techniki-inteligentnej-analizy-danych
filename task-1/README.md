# About

This project is an application for converting table-like `.xlsx` files into `.docx` and `.pdf` files with two options for opinionated formating.

## Tech stack
+ **Backend:** Python + Flask + pyinstaller
+ **Frontend:** HTML + CSS + JS

App comes bundled in a single `.exe` file with integrated `Werkzeug’s development server` inside.

# Build

## Requirements

1. Latest version of [uv project manager](https://docs.astral.sh/uv/)

## Steps

1. Clone the repository to your current directory
    ```
    git clone https://github.com/kacpermajkowski/techniki-inteligentnej-analizy-danych.git .
    ```
2. Go into project directory
    ```
    cd task-1
    ```
3.  Install required Python version, create virtual environment and install dependencies
    ```
    uv sync
    ```
4. Ways to run:
    - Start a development server
        ```
        uv run main.py
        ```
    - Build and run an `.exe`
        1. Build
            ```
            uv run pyinstaller main.spec
            ```
        2. Executable will be at `/dist/main.exe`

# Usage

1. Find and download desired executable version from [GitHub Releases](https://github.com/kacpermajkowski/techniki-inteligentnej-analizy-danych/releases)
2. Run the executable. The app will start in your default browser in a few seconds.
3. The web app will guide you through the options and conversion process.
4. After you're done with conversions, simply close the tab and local server running in the background will close automatically after 60 seconds.