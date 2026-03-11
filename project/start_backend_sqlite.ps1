$env:USE_SQLITE = "1"
$env:MYSQL_DATABASE = "zhongyao"
$env:MYSQL_USER = "root"
$env:MYSQL_PASSWORD = "123456"
$env:MYSQL_HOST = "127.0.0.1"
$env:MYSQL_PORT = "3306"
$env:FRONTEND_ORIGINS = "http://127.0.0.1:5173,http://localhost:5173,http://127.0.0.1:5175,http://localhost:5175"

Write-Host "Starting Django backend with SQLite..." -ForegroundColor Cyan
python manage.py runserver
