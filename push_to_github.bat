@echo off
chcp 65001 > nul
echo ========================================
echo    RAG智能问答系统 - Git推送脚本
echo ========================================
echo.

REM 检查Git是否安装
where git > nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到Git
    echo.
    echo 请先安装Git:
    echo   1. 访问 https://git-scm.com/download/win
    echo   2. 下载并安装Git for Windows
    echo   3. 安装完成后重新运行此脚本
    echo.
    pause
    exit /b 1
)

echo [信息] Git版本:
git --version
echo.

REM 设置Git配置（如果未设置）
git config user.name > nul 2>&1
if errorlevel 1 (
    echo [提示] 首次使用Git，需要配置用户信息
    set /p username="请输入你的Git用户名: "
    set /p email="请输入你的Git邮箱: "
    git config --global user.name "%username%"
    git config --global user.email "%email%"
    echo.
)

REM 初始化Git仓库（如果尚未初始化）
if not exist ".git" (
    echo [步骤1] 初始化Git仓库...
    git init
    git branch -M main
) else (
    echo [步骤1] Git仓库已存在
)

REM 添加远程仓库
echo [步骤2] 添加远程仓库...
git remote remove origin 2>nul
git remote add origin https://github.com/Yuch666/RAG-QA-System-ych-31.git

REM 添加所有文件
echo [步骤3] 添加文件到暂存区...
git add .

REM 提交
echo [步骤4] 提交更改...
set commit_msg=RAG智能问答系统 - 完整项目代码
git commit -m "%commit_msg%"

REM 推送到GitHub
echo [步骤5] 推送到GitHub...
git push -u origin main

if errorlevel 1 (
    echo.
    echo [错误] 推送失败！
    echo.
    echo 可能的原因：
    echo 1. 网络连接问题
    echo 2. 需要登录GitHub（输入用户名和Token）
    echo 3. Token权限不足
    echo.
    echo 解决方法：
    echo - 如果要求输入密码，请使用GitHub Personal Access Token
    echo - Token生成地址: https://github.com/settings/tokens
    echo - 需要勾选 'repo' 权限
    echo.
) else (
    echo.
    echo ========================================
    echo    推送成功！
    echo ========================================
    echo.
    echo 仓库地址: https://github.com/Yuch666/RAG---QA---System----2405030331
    echo.
)

pause