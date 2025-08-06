# ==============================================================================
# Setup Proxy Environment Variables
# ==============================================================================
# Purpose: Set up environment variables for proxy configuration
# ==============================================================================

Write-Host "🔧 Setting up proxy environment variables..." -ForegroundColor Green

# Set proxy provider
$env:PROXY_PROVIDER = "tor"

# Set Tor configuration
$env:TOR_HOST = "127.0.0.1"
$env:TOR_PORT = "9050"
$env:TOR_CONTROL_PORT = "9051"
$env:TOR_CONTROL_PASSWORD = "my_control_password_123"

# Set proxy session settings
$env:PROXY_SESSION_DURATION = "600"
$env:PROXY_MAX_REQUESTS = "100"
$env:PROXY_RETRY_ATTEMPTS = "3"
$env:PROXY_TIMEOUT = "30"

# Verify settings
Write-Host "✅ Environment variables set:" -ForegroundColor Green
Write-Host "   PROXY_PROVIDER: $env:PROXY_PROVIDER"
Write-Host "   TOR_HOST: $env:TOR_HOST"
Write-Host "   TOR_PORT: $env:TOR_PORT"
Write-Host "   TOR_CONTROL_PORT: $env:TOR_CONTROL_PORT"
Write-Host "   TOR_CONTROL_PASSWORD: $env:TOR_CONTROL_PASSWORD"

Write-Host "`n⚠️  IMPORTANT: You need to configure Tor to enable the control port!" -ForegroundColor Yellow
Write-Host "   Add these lines to your torrc file:" -ForegroundColor Yellow
Write-Host "   ControlPort 9051" -ForegroundColor Cyan
Write-Host "   HashedControlPassword 16:XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX" -ForegroundColor Cyan
Write-Host "   CookieAuthentication 0" -ForegroundColor Cyan

Write-Host "`n💡 To generate the hashed password, run:" -ForegroundColor Blue
Write-Host "   tor --hash-password 'my_control_password_123'" -ForegroundColor Cyan

Write-Host "`n🔄 After updating torrc, restart Tor for changes to take effect." -ForegroundColor Yellow 