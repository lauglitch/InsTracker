# CLEAN ONLY FREE
Remove-Item -Recurse -Force build -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force dist\free -ErrorAction SilentlyContinue

# BUILD
pyinstaller `
--clean `
--noconfirm `
--onefile `
--windowed `
--noupx `
--paths "." `
--distpath dist\free `
--name "InsTracker_Free" `
--add-data "Assets;Assets" `
free/app.py

# README
Copy-Item README.txt dist\free\README.txt

# ZIP
Compress-Archive `
-Path dist\free\InsTracker_Free.exe, dist\free\README.txt `
-DestinationPath dist\free\InsTracker_Free.zip `
-Force