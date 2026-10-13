@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ============================================
echo   Уральский лес - запуск сайта на localhost
echo ============================================
echo.
echo [1/4] Установка зависимостей...
python -m pip install -r requirements.txt
if errorlevel 1 goto error

echo.
echo [2/4] Миграции базы данных...
python manage.py migrate
if errorlevel 1 goto error

echo.
echo [3/4] Первичная настройка (админ, категории, контент)...
python manage.py init_site --with-demo
if errorlevel 1 goto error

echo.
echo [4/4] Запуск сервера...
echo.
echo   Сайт:    http://127.0.0.1:8000/
echo   Админка: http://127.0.0.1:8000/admin/
echo   Логин:   admin
echo   Пароль:  UralForest2026!
echo.
python manage.py runserver
goto end

:error
echo.
echo Произошла ошибка. Проверьте, установлен ли Python и доступен ли интернет.

:end
pause
