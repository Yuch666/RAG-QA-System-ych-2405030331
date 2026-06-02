@echo off
chcp 65001 > nul
echo ========================================
echo    RAG智能问答系统打包脚本
echo ========================================
echo.

REM 检查虚拟环境
if not exist "venv\Scripts\python.exe" (
    echo [错误] 未找到Python虚拟环境
    echo 请先运行 install.bat 安装环境
    pause
    exit /b 1
)

REM 激活虚拟环境
call venv\Scripts\activate

REM 检查PyInstaller
pip show pyinstaller > nul 2>&1
if errorlevel 1 (
    echo [步骤1] 安装PyInstaller...
    pip install pyinstaller
)

echo.
echo [步骤2] 开始打包应用...
echo 注意：Streamlit应用打包可能需要较长时间
echo.

REM 创建打包目录结构
if not exist "dist" mkdir dist
if not exist "build" mkdir build

REM 打包为目录模式（更稳定）
pyinstaller --noconfirm --clean \
    --windowed \
    --name "RAG-QA-System" \
    --add-data "config.py;." \
    --add-data "knowledge_base.py;." \
    --collect-all streamlit \
    --collect-all langchain \
    --collect-all langchain_community \
    --collect-all chromadb \
    --hidden-import "pypdf2" \
    --hidden-import "docx2txt" \
    --hidden-import "tiktoken" \
    --hidden-import "sentence_transformers" \
    app.py

if errorlevel 1 (
    echo [错误] 打包失败
    pause
    exit /b 1
)

echo.
echo ========================================
echo    打包完成！
echo ========================================
echo.
echo 打包结果位于 dist\RAG-QA-System 目录
echo.
echo 注意事项：
echo 1. exe文件运行仍需要目标机器安装Ollama
echo 2. 目标机器需要下载所需模型
echo 3. 建议使用便携式部署包方式（更稳定）
echo.
echo 如需创建便携式部署包，请运行：
echo create_portable.bat
echo.
pause