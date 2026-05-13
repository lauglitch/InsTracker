$version = "1.3.3"

Write-Host "==============================="
Write-Host " PUSH FREE"
Write-Host "==============================="

if (!(Test-Path "dist\InsTracker_Free")) {
    Write-Host "ERROR: FREE build not found"
    exit 1
}

butler push "dist\InsTracker_Free" lauglitch/instracker:free-windows --userversion $version

if ($LASTEXITCODE -ne 0) {
    Write-Host "FREE PUSH FAILED"
    exit 1
}

Write-Host "==============================="
Write-Host " PUSH PRO"
Write-Host "==============================="

if (!(Test-Path "dist\InsTracker_Pro")) {
    Write-Host "ERROR: PRO build not found"
    exit 1
}

butler push "dist\InsTracker_Pro" lauglitch/instracker:pro-windows --userversion $version

if ($LASTEXITCODE -ne 0) {
    Write-Host "PRO PUSH FAILED"
    exit 1
}

Write-Host "==============================="
Write-Host " PUSH COMPLETED SUCCESSFULLY"
Write-Host "==============================="