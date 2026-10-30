@echo off
cd /d "%~dp0"
docker info >nul 2>&1
if errorlevel 1 (
  echo Docker Desktop is not ready. Start Docker Desktop with Linux containers, then try again.
  pause
  exit /b 1
)
if not exist .env copy .env.example .env >nul
docker compose up -d --build --wait --wait-timeout 180
if errorlevel 1 (
  echo Startup failed. Run: docker compose logs --tail 50
  pause
  exit /b 1
)
echo Ready. Default URL: http://127.0.0.1:8765
echo Teaching files: teacher_workspace\published
echo Stop: docker compose stop
for /f "delims=" %%U in ('docker compose port teacher 8765') do start "" "http://%%U"
pause
