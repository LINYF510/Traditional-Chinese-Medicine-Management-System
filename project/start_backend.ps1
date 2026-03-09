param(
    [string]$Database = "zhongyao",
    [string]$User = "root",
    [string]$Password = "123456",
    [string]$DbHost = "127.0.0.1",
    [string]$DbPort = "3306",
    [string]$RunHost = "127.0.0.1",
    [string]$RunPort = "8000",
    [switch]$NoRunServer
)

$ErrorActionPreference = "Stop"

Write-Host "[1/6] Configure MySQL env vars..." -ForegroundColor Cyan
$env:MYSQL_DATABASE = $Database
$env:MYSQL_USER = $User
$env:MYSQL_PASSWORD = $Password
$env:MYSQL_HOST = $DbHost
$env:MYSQL_PORT = $DbPort

Write-Host "[2/6] Check mysql client..." -ForegroundColor Cyan
Get-Command mysql -ErrorAction Stop | Out-Null

Write-Host "[3/6] Ensure database exists..." -ForegroundColor Cyan
$createDbSql = "CREATE DATABASE IF NOT EXISTS $Database DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
$mysqlArgs = @(
    "-u", $User,
    "-p$Password",
    "-h", $DbHost,
    "-P", $DbPort,
    "-e", $createDbSql
)
& mysql @mysqlArgs

Write-Host "[4/6] Run migrations..." -ForegroundColor Cyan
python manage.py migrate --noinput

Write-Host "[5/6] Seed demo data..." -ForegroundColor Cyan
python manage.py seed_demo

if ($NoRunServer) {
    Write-Host "[6/6] Skip runserver (NoRunServer enabled)." -ForegroundColor Yellow
    exit 0
}

Write-Host "[6/6] Start Django server..." -ForegroundColor Cyan
python manage.py runserver "$RunHost`:$RunPort"
