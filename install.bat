@echo off
chcp 65001 > nul
echo ========================================
echo    RAG智能问答系统安装脚本
echo ========================================
echo.

REM 检查Python
python --version > nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到Python
    echo 请先安装Python 3.9或更高版本
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [信息] Python版本:
python --version
echo.

echo [步骤1] 创建虚拟环境...
python -m venv venv
if errorlevel 1 (
    echo [错误] 创建虚拟环境失败
    pause
    exit /b 1
)
echo [完成] 虚拟环境创建成功
echo.

echo [步骤2] 激活虚拟环境...
call venv\Scripts\activate
echo [完成] 虚拟环境已激活
echo.

echo [步骤3] 升级pip...
python -m pip install --upgrade pip
echo.

echo [步骤4] 安装依赖包...
echo 这可能需要几分钟时间，请耐心等待...
pip install -r requirements.txt
if errorlevel 1 (
    echo [错误] 安装依赖失败
    echo 请检查requirements.txt文件是否存在
    pause
    exit /b 1
)
echo [完成] 依赖包安装成功
echo.

echo [步骤5] 创建文档目录...
if not exist "documents" mkdir documents
echo [完成] documents目录已创建
echo.

echo [步骤6] 创建向量数据库目录...
if not exist "chroma_db" mkdir chroma_db
echo [完成] chroma_db目录已创建
echo.

echo ========================================
echo    安装完成！
echo ========================================
echo.
echo 后续步骤：
echo.
echo 1. 安装Ollama
echo    下载地址: https://ollama.com/
echo    安装后运行: ollama serve
echo.
echo 2. 下载对话模型
echo    命令: ollama pull deepseek-r1:7b
echo    或: ollama pull qwen2:7b
echo.
echo 3. 下载嵌入模型
echo    命令: ollama pull nomic-embed-text
echo.
echo 4. 将PDF或DOCX文档放入 documents 目录
echo    至少需要5份文档用于测试
echo.
echo 5. 运行 start.bat 启动应用
echo.
echo ========================================
pause