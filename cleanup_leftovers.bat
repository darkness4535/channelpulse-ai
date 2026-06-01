@echo off
REM Удаляет остатки browser/fingerprint (закройте браузер-сервер и Cursor, если не удаляется)
cd /d "%~dp0"
echo Removing node_modules and tools...
rd /s /q node_modules 2>nul
rd /s /q tools 2>nul
if exist node_modules (echo node_modules: часть файлов занята — перезагрузите ПК или удалите вручную) else (echo node_modules: OK)
if exist tools (echo tools: часть файлов занята) else (echo tools: OK)
pause
