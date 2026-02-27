@echo off
:: update-gallery.bat — Run from the ArtistWebPage folder
::
:: Double-click this file to regenerate image-manifest.json
:: after adding or removing images in the images/ folder.
::
:: Requires Python 3 (https://python.org) — no packages to install.
:: If you push images to GitHub instead, the Action does this for you.

set PYTHON=
where python  >nul 2>&1 && set PYTHON=python
where python3 >nul 2>&1 && set PYTHON=python3

if "%PYTHON%"=="" (
    echo ERROR: Python is not installed or not on PATH.
    echo Download it from https://python.org
    pause
    exit /b 1
)

%PYTHON% generate-manifest.py
echo.
echo Done! Refresh index.html in your browser to see the updated gallery.
pause
