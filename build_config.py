"""
任务5：本地化打包配置
使用PyInstaller将Streamlit应用打包成独立的exe可执行文件

AI生成说明：本打包脚本由AI辅助生成，用于配置PyInstaller打包参数
"""

# PyInstaller打包命令
# 注意：Streamlit应用打包较为复杂，以下是推荐的打包方式

# 方式一：使用stlite（Streamlit官方打包方案）
# pip install stlite
# stlite build app.py --output dist

# 方式二：使用PyInstaller（传统方式）
# pyinstaller --onefile --windowed --name "RAG-QA-System" app.py

# 推荐的打包步骤：

"""
打包前准备：
1. 确保所有依赖已安装
2. 确保Ollama服务已安装并下载了模型
3. 测试应用运行正常

打包命令：
"""

# 创建打包脚本
PACK_COMMAND = """
# 步骤1：安装打包工具
pip install pyinstaller

# 步骤2：创建打包配置文件
# 在项目目录下运行以下命令

pyinstaller --onefile \
    --windowed \
    --name "RAG-QA-System" \
    --add-data "config.py;." \
    --add-data "knowledge_base.py;." \
    --add-data "rag_qa_cli.py;." \
    --hidden-import "streamlit" \
    --hidden-import "langchain" \
    --hidden-import "langchain_community" \
    --hidden-import "chromadb" \
    --hidden-import "pypdf2" \
    --hidden-import "docx2txt" \
    --hidden-import "tiktoken" \
    app.py

# 步骤3：打包完成后，exe文件位于dist目录
"""

# 注意事项
NOTES = """
注意事项：
1. Streamlit应用打包较为复杂，推荐使用以下替代方案：

方案A：使用便携式Python环境
- 将整个Python环境和项目打包成压缩包
- 用户解压后运行启动脚本
- 这种方式最稳定可靠

方案B：使用stlite（Web打包）
- 将Streamlit应用打包成静态网页
- 用户通过浏览器访问
- 需要配合本地Ollama服务

方案C：创建启动脚本
- 创建一个批处理文件(.bat)启动应用
- 用户双击运行即可
"""

# 创建便携式启动脚本
PORTABLE_SCRIPT = """
@echo off
echo ========================================
echo    RAG智能问答系统启动器
echo ========================================
echo.

REM 检查Python环境
if not exist "venv\\Scripts\\python.exe" (
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
    echo 请先启动Ollama服务（运行 ollama serve）
    echo.
    choice /c YN /m "是否继续启动应用？"
    if errorlevel 2 exit /b 0
)

echo [启动] 正在启动RAG问答系统...
echo.
echo 应用将在浏览器中打开
echo 请勿关闭此窗口
echo.

REM 激活虚拟环境并启动应用
call venv\\Scripts\\activate
streamlit run app.py --server.headless true

pause
"""

# 创建安装脚本
INSTALL_SCRIPT = """
@echo off
echo ========================================
echo    RAG智能问答系统安装脚本
echo ========================================
echo.

REM 检查Python
python --version > nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到Python
    echo 请先安装Python 3.9+
    pause
    exit /b 1
)

echo [步骤1] 创建虚拟环境...
python -m venv venv
if errorlevel 1 (
    echo [错误] 创建虚拟环境失败
    pause
    exit /b 1
)

echo [步骤2] 激活虚拟环境...
call venv\\Scripts\\activate

echo [步骤3] 安装依赖包...
pip install -r requirements.txt
if errorlevel 1 (
    echo [错误] 安装依赖失败
    pause
    exit /b 1
)

echo [步骤4] 创建文档目录...
if not exist "documents" mkdir documents

echo.
echo ========================================
echo    安装完成！
echo ========================================
echo.
echo 后续步骤：
echo 1. 安装Ollama: https://ollama.com/
echo 2. 下载模型: ollama pull deepseek-r1:7b
echo 3. 下载嵌入模型: ollama pull nomic-embed-text
echo 4. 将PDF/DOCX文档放入 documents 目录
echo 5. 运行 start.bat 启动应用
echo.
pause
"""

# 创建完整的打包说明文档
BUILD_GUIDE = """
# 本地化打包指南

## 推荐方案：便携式部署包

由于Streamlit应用的特殊性，推荐使用便携式部署包而非exe文件。

### 打包步骤

1. 准备项目文件
   - 确保所有代码文件完整
   - 确保requirements.txt正确

2. 创建便携式包结构
   ```
   RAG-QA-System-Portable/
   ├── app.py
   ├── config.py
   ├── knowledge_base.py
   ├── rag_qa_cli.py
   ├── test_ollama.py
   ├── requirements.txt
   ├── README.md
   ├── install.bat
   ├── start.bat
   └── documents/
   ```

3. 用户使用流程
   - 解压便携式包
   - 运行 install.bat 安装环境
   - 安装Ollama并下载模型
   - 将文档放入documents目录
   - 运行 start.bat 启动应用

### exe打包（可选）

如果确实需要exe文件，可以使用以下方法：

```bash
# 安装打包工具
pip install pyinstaller

# 打包（单文件模式）
pyinstaller --onefile --windowed --name "RAG-QA-System" app.py

# 打包（目录模式，更稳定）
pyinstaller --windowed --name "RAG-QA-System" app.py
```

注意：exe打包后仍需要：
- 目标机器安装Ollama服务
- 目标机器已下载所需模型
"""

print(BUILD_GUIDE)