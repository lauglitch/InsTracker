# CLEAN ONLY PRO
Remove-Item -Recurse -Force build -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force dist\pro -ErrorAction SilentlyContinue

# BUILD
pyinstaller `
--clean `
--noconfirm `
--onefile `
--windowed `
--noupx `
--paths "." `
--distpath dist\pro `
--name "InsTracker_Pro" `
--add-data "Assets;Assets" `
pro/app.py

# README
Copy-Item README.txt dist\pro\README.txt

# CREATE FOLLOWIGNORE
New-Item `
-Path dist\pro\followignore.txt `
-ItemType File `
-Force

# ZIP
Compress-Archive `
-Path dist\pro\InsTracker_Pro.exe,
      dist\pro\README.txt,
      dist\pro\followignore.txt `
-DestinationPath dist\pro\InsTracker_Pro.zip `
-Force