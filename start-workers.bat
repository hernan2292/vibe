@echo off
REM Script para iniciar múltiples workers de Laravel Queue en Windows
REM Para sincronización LDAP paralela

echo ========================================
echo  Laravel Queue Workers - LDAP Sync
echo ========================================
echo.

REM Configuración
set WORKERS=24
set PHP_PATH=php
set ARTISAN_PATH=%~dp0artisan

echo Iniciando %WORKERS% workers paralelos...
echo.

REM Iniciar workers en ventanas separadas (sin --name, no existe en Laravel 7)
for /L %%i in (1,1,%WORKERS%) do (
    start "LDAP Worker %%i" cmd /k "%PHP_PATH% %ARTISAN_PATH% queue:work --timeout=180 --tries=3 --sleep=1"
    echo [OK] Worker %%i iniciado
    timeout /t 1 /nobreak >nul
)

echo.
echo ========================================
echo  %WORKERS% workers iniciados exitosamente!
echo ========================================
echo.
echo Para monitorear el progreso:
echo   php artisan ldap:sync-status {batch_id}
echo.
echo Para detener todos los workers:
echo   1. Cerrar todas las ventanas "LDAP Worker"
echo   2. O ejecutar: php artisan queue:restart
echo.
pause
