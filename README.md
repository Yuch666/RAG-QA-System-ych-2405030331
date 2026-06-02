# RAG智能问答系统

基于本地知识库的检索增强生成(RAG)智能问答系统，使用Ollama本地大模型、LangChain框架和Streamlit构建，能够"学习"指定本地文档并回答相关问题。

## 项目简介

本项目实现了一个完整的RAG问答系统，支持：
- 📁 上传PDF/DOCX文档构建本地知识库
- 🔍 基于向量检索的智能问答
- 💬 多轮对话记忆
- 🖥️ 美观的Web交互界面
- 🔒 完全本地化运行，无需联网

## 环境要求

### 系统要求
- Windows 10/11
- Python 3.9+ (推荐3.10或3.11)
- 至少8GB内存（推荐16GB用于运行7B模型）
- 约10GB磁盘空间（用于存储模型和向量库）

### 软件依赖
- Ollama (用于运行本地大模型)
- Python虚拟环境

## 安装步骤

### 1. 安装Ollama

1. 访问 [Ollama官网](https://ollama.com/) 下载Windows版本
2. 运行安装程序完成安装
3. 打开命令行，下载所需模型：

```bash
# 下载对话模型（选择其一）
ollama pull deepseek-r1:7b
# 或
ollama pull qwen2:7b

# 下载嵌入模型
ollama pull nomic-embed-text
```

### 2. 创建Python虚拟环境

```bash
# 克隆项目（或下载源码）
git clone https://github.com/你的用户名/RAG-QA-System-姓名-学号.git
cd RAG-QA-System-姓名-学号

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

### 3. 验证环境配置

```bash
# 运行测试脚本
python test_ollama.py
```

确保所有测试通过后再继续。

## 使用说明

### 方式一：Web应用（推荐）

```bash
# 启动Streamlit应用
streamlit run app.py
```

应用将在浏览器中打开（默认地址：http://localhost:8501）

#### Web应用操作流程：

1. **上传文档**
   - 在"文档管理"标签页点击上传按钮
   - 选择PDF或DOCX文件（支持多文件上传）

2. **构建知识库**
   - 点击"构建知识库"按钮
   - 等待文档处理完成（分块、向量化）

3. **开始问答**
   - 切换到"问答交互"标签页
   - 输入问题，点击"提问"
   - 查看回答和参考来源

4. **查看历史**
   - 对话历史自动保存
   - 可随时查看多轮问答记录

### 方式二：命令行版本

```bash
# 运行命令行版本
python rag_qa_cli.py

# 运行测试模式
python rag_qa_cli.py --test
```

命令行交互命令：
- 输入问题进行问答
- `history` - 查看对话历史
- `stats` - 查看系统状态
- `clear` - 清空对话历史
- `quit` - 退出系统

## 项目结构

```
RAG-QA-System-姓名-学号/
│
├── app.py                 # Streamlit Web应用主程序
├── rag_qa_cli.py          # 命令行版本RAG问答系统
├── knowledge_base.py      # 知识库构建模块
├── config.py              # 配置文件
├── test_ollama.py         # 环境测试脚本
├── requirements.txt       # 依赖包列表
├── README.md              # 项目说明文档
├── .gitignore             # Git忽略配置
│
├── documents/             # 文档存储目录（需自行创建）
│   └── *.pdf, *.docx      # 知识库文档
│
├── chroma_db/             # 向量数据库（自动生成）
│
└── screenshots/           # 效果截图目录
    ├── interface.png
    ├── upload.png
    └── qa_example.png
```

## 关键技术点

### RAG流程

1. **文档加载**：使用PyPDFLoader和Docx2txtLoader解析文档
2. **文本分块**：RecursiveCharacterTextSplitter（chunk_size=1000, overlap=200）
3. **向量嵌入**：Ollama nomic-embed-text模型
4. **向量存储**：Chroma向量数据库
5. **相似检索**：基于余弦相似度返回top-k相关文档
6. **答案生成**：DeepSeek-R1/Qwen2模型基于检索内容生成回答

### 所用模型

| 模型类型 | 模型名称 | 说明 |
|---------|---------|------|
| 对话模型 | deepseek-r1:7b | DeepSeek推理模型，擅长逻辑推理 |
| 对话模型 | qwen2:7b | 阿里通义千问，中文能力强 |
| 嵌入模型 | nomic-embed-text | 高效文本嵌入模型 |
| 嵌入模型 | all-minilm | 轻量级嵌入模型 |

### 技术框架

- **LangChain**: RAG链构建、文档处理
- **ChromaDB**: 向量数据库存储
- **Streamlit**: Web界面开发
- **Ollama**: 本地模型推理服务

## 项目效果截图

### 界面截图

![系统界面](screenshots/interface.png)
*系统主界面展示*

![文档上传](screenshots/upload.png)
*文档上传与知识库构建*

![问答示例](screenshots/qa_example.png)
*问答交互示例*

### 问答效果示例

**问题：什么是自然语言处理？**

**回答：**
自然语言处理（Natural Language Processing，简称NLP）是人工智能的重要分支，它研究如何让计算机理解、解释和生成人类语言。NLP结合了计算机科学、语言学和机器学习等多个领域的知识，旨在实现人与计算机之间的自然语言交互...

**参考来源：**
- NLP技术概述.pdf
- 自然语言处理基础.docx

## 已知问题与改进方向

### 已知问题

1. 首次加载模型可能较慢（需要预热）
2. 大文件上传时内存占用较高
3. 某些特殊格式的PDF可能解析不完整

### 改进方向

1. ✨ 支持更多文档格式（TXT、Markdown等）
2. ✨ 添加批量文档上传功能
3. ✨ 实现问答记录导出功能
4. ✨ 添加夜间模式切换
5. ✨ 支持多语言问答
6. ✨ 添加文档预览功能

## AI使用日志

本项目使用Trae AI辅助开发，主要辅助内容：

| 功能模块 | AI辅助内容 | 修改说明 |
|---------|-----------|---------|
| test_ollama.py | 环境测试脚本框架 | 根据实际需求调整测试项 |
| knowledge_base.py | 文档处理和向量存储逻辑 | 优化分块参数和检索逻辑 |
| rag_qa_cli.py | RAG问答链构建 | 自定义提示词模板 |
| app.py | Streamlit界面布局 | 调整UI样式和交互逻辑 |
| config.py | 配置参数设计 | 根据项目需求调整参数 |

## 许可证

本项目仅供学习和研究使用。

## 致谢

- [Ollama](https://ollama.com/) - 本地大模型运行平台
- [LangChain](https://python.langchain.com/) - RAG框架
- [Streamlit](https://docs.streamlit.io/) - Web应用框架
- [ChromaDB](https://www.trychroma.com/) - 向量数据库

---

**作者：** Yuch
**学号：** 2405030331
**日期：** 2026年6月