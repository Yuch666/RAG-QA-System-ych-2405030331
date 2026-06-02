# 配置文件 - 存储所有配置参数

# Ollama模型配置
OLLAMA_BASE_URL = "http://localhost:11434"
MODEL_NAME = "deepseek-r1:7b"  # 可选: qwen2:7b
EMBEDDING_MODEL = "nomic-embed-text"  # 可选: all-minilm

# 文档处理配置
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

# 向量数据库配置
CHROMA_PERSIST_DIR = "./chroma_db"
CHROMA_COLLECTION_NAME = "rag_knowledge_base"

# 文档存储目录
DOCUMENTS_DIR = "./documents"

# 检索配置
RETRIEVER_K = 3  # 返回最相关的3个文本块

# 系统提示词
SYSTEM_PROMPT = """你是一个专业的问答助手。请基于提供的参考文档回答用户问题。

重要规则：
1. 只使用参考文档中的信息回答问题
2. 如果文档中没有相关信息，请明确回答"文档中未找到相关答案"
3. 不要编造或推测答案
4. 如果答案来自文档，请简洁准确地引用相关内容
5. 保持回答的专业性和准确性

参考文档内容：
{context}

用户问题：{question}

请基于以上参考文档回答："""