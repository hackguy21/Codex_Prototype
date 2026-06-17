$ProjectDir = "C:\Users\hyseong97\Documents\ProjectHormuz"

Set-Location $ProjectDir

Write-Host "Current directory:"
Write-Host (Get-Location)
Write-Host ""

Write-Host "Python version:"
py -3.12 --version
Write-Host ""

Write-Host "Starting Project Hormuz..."
Write-Host "Open this URL in your browser:"
Write-Host "http://127.0.0.1:8000"
Write-Host ""

py -3.12 .\main.py

Write-Host ""
Write-Host "Project Hormuz has stopped."
Read-Host "Press Enter to close"
