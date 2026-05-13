# Clean inicial (opcional pero seguro)
Remove-Item -Recurse -Force build, dist -ErrorAction SilentlyContinue

Write-Host "==============================="
Write-Host " BUILD FREE"
Write-Host "==============================="

.\build_free.ps1

if ($LASTEXITCODE -ne 0) {
    Write-Host "FREE BUILD FAILED - STOPPING RELEASE"
    exit 1
}

Write-Host "==============================="
Write-Host " BUILD PRO"
Write-Host "==============================="

.\build_pro.ps1

if ($LASTEXITCODE -ne 0) {
    Write-Host "PRO BUILD FAILED - STOPPING RELEASE"
    exit 1
}

Write-Host "==============================="
Write-Host " VERIFY OUTPUTS"
Write-Host "==============================="

if (!(Test-Path "dist\InsTracker_Free") -or !(Test-Path "dist\InsTracker_Pro")) {
    Write-Host "BUILD OUTPUTS MISSING"
    exit 1
}

Write-Host "==============================="
Write-Host " DONE - ALL BUILDS SUCCESSFUL"
Write-Host "==============================="