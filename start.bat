@echo off
chcp 65001 > nul
echo ========================================
echo    RAG智能问答系统启动器
echo ========================================
echo.

REM 检查虚拟环境
if not exist "venv\Scripts\python.exe" (
    echo [错误] 未找到Python虚拟环境
    echo 请先运行 install.bat 安装环境
    pause
    exit /b 1
)

REM 检查Ollama服务
echo [检查] 正在检查Ollama服务...
curl -s http://localhost:11434 > nul 2>&1
if errorlevel 1 (
    echo [警告] Ollama服务未启动
    echo 请确保Ollama已安装并正在运行
    echo 启动命令: ollama serve
    echo.
    set /p continue="是否继续启动应用？(Y/N): "
    if /i not "%continue%"=="Y" exit /b 0
)

echo.
echo [信息] 正在启动RAG问答系统...
echo [信息] 应用将在浏览器中自动打开
echo [信息] 请勿关闭此窗口，关闭窗口将停止应用
echo.
echo ========================================
echo.

REM 激活虚拟环境
call venv\Scripts\activate

REM 启动Streamlit应用
streamlit run app.py --server.headless true --server.port 8501

echo.
echo [信息] 应用已停止
pause