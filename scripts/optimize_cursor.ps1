#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Optimize Cursor IDE performance for the aggregator project
    
.DESCRIPTION
    This script helps optimize Cursor's performance by:
    1. Clearing Cursor cache
    2. Removing Python cache files
    3. Providing restart instructions
    
.NOTES
    Run this script when Cursor is running slowly
#>

param(
    [switch]$ClearCache,
    [switch]$RestartCursor
)

Write-Host "🚀 Cursor Performance Optimizer" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Green

# Get project root
$projectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $projectRoot

if ($ClearCache) {
    Write-Host "`n🧹 Clearing Cursor cache..." -ForegroundColor Yellow
    
    # Clear Cursor cache directory
    $cursorCache = Join-Path $projectRoot ".cursor"
    if (Test-Path $cursorCache) {
        Remove-Item -Path $cursorCache -Recurse -Force -ErrorAction SilentlyContinue
        Write-Host "   ✅ Cleared .cursor cache" -ForegroundColor Green
    } else {
        Write-Host "   ℹ️  No .cursor cache found" -ForegroundColor Blue
    }
    
    # Clear Python cache
    Write-Host "`n🐍 Clearing Python cache..." -ForegroundColor Yellow
    $pyCacheDirs = Get-ChildItem -Path $projectRoot -Recurse -Directory -Name "__pycache__" -ErrorAction SilentlyContinue
    foreach ($cacheDir in $pyCacheDirs) {
        $fullPath = Join-Path $projectRoot $cacheDir
        Remove-Item -Path $fullPath -Recurse -Force -ErrorAction SilentlyContinue
        Write-Host "   ✅ Cleared: $cacheDir" -ForegroundColor Green
    }
    
    # Clear .pyc files
    $pycFiles = Get-ChildItem -Path $projectRoot -Recurse -File -Filter "*.pyc" -ErrorAction SilentlyContinue
    foreach ($pycFile in $pycFiles) {
        Remove-Item -Path $pycFile.FullName -Force -ErrorAction SilentlyContinue
        Write-Host "   ✅ Cleared: $($pycFile.Name)" -ForegroundColor Green
    }
}

Write-Host "`n📋 Performance Optimization Summary:" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan

# Check if .cursorignore exists
$cursorIgnore = Join-Path $projectRoot ".cursorignore"
if (Test-Path $cursorIgnore) {
    Write-Host "   ✅ .cursorignore file found" -ForegroundColor Green
} else {
    Write-Host "   ❌ .cursorignore file missing" -ForegroundColor Red
}

# Check large directories
Write-Host "`n📁 Large directories that may affect performance:" -ForegroundColor Yellow
$largeDirs = @(
    @{Name=".venv"; Path=".venv"},
    @{Name="baselines"; Path="baselines"},
    @{Name="changes"; Path="changes"},
    @{Name="comparison_results"; Path="comparison_results"},
    @{Name="output"; Path="output"}
)

foreach ($dir in $largeDirs) {
    $dirPath = Join-Path $projectRoot $dir.Path
    if (Test-Path $dirPath) {
        $size = (Get-ChildItem $dirPath -Recurse -File -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum
        $sizeMB = [math]::Round($size / 1MB, 2)
        Write-Host "   📊 $($dir.Name): $sizeMB MB" -ForegroundColor $(if ($sizeMB -gt 10) { "Red" } else { "Green" })
    }
}

Write-Host "`n💡 Performance Tips:" -ForegroundColor Cyan
Write-Host "===================" -ForegroundColor Cyan
Write-Host "1. Close Cursor completely" -ForegroundColor White
Write-Host "2. Delete the .cursor folder if it exists" -ForegroundColor White
Write-Host "3. Restart Cursor" -ForegroundColor White
Write-Host "4. The .cursorignore file will prevent indexing large directories" -ForegroundColor White
Write-Host "5. Consider moving large JSON files to a separate data directory" -ForegroundColor White

if ($RestartCursor) {
    Write-Host "`n🔄 Restarting Cursor..." -ForegroundColor Yellow
    
    # Try to close Cursor processes
    $cursorProcesses = Get-Process -Name "Cursor" -ErrorAction SilentlyContinue
    if ($cursorProcesses) {
        Write-Host "   Closing Cursor processes..." -ForegroundColor Yellow
        $cursorProcesses | Stop-Process -Force
        Start-Sleep -Seconds 2
    }
    
    # Start Cursor
    Write-Host "   Starting Cursor..." -ForegroundColor Yellow
    Start-Process "Cursor"
}

Write-Host "`n✅ Optimization complete!" -ForegroundColor Green
Write-Host "Cursor should now run much faster." -ForegroundColor Green 