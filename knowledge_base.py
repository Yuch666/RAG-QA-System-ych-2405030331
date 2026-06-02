"""
任务2：构建本地知识库模块
该模块实现文档加载、文本分块、向量化和检索功能

AI生成说明：本模块由AI辅助生成，实现了LangChain文档处理的核心功能
"""

import os
import sys
from typing import List, Optional
from pathlib import Path

# LangChain相关导入
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OllamaEmbeddings
from langchain.schema import Document

# 导入配置
from config import (
    CHUNK_SIZE, 
    CHUNK_OVERLAP, 
    EMBEDDING_MODEL,
    OLLAMA_BASE_URL,
    CHROMA_PERSIST_DIR,
    CHROMA_COLLECTION_NAME,
    RETRIEVER_K
)


class KnowledgeBase:
    """本地知识库管理类"""
    
    def __init__(self, persist_directory: str = CHROMA_PERSIST_DIR):
        """
        初始化知识库
        
        Args:
            persist_directory: 向量数据库持久化目录
        """
        self.persist_directory = persist_directory
        self.embeddings = None
        self.vectorstore = None
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
        
        # 初始化嵌入模型
        self._init_embeddings()
        
    def _init_embeddings(self):
        """初始化Ollama嵌入模型"""
        try:
            self.embeddings = OllamaEmbeddings(
                model=EMBEDDING_MODEL,
                base_url=OLLAMA_BASE_URL
            )
            print(f"✅ 嵌入模型初始化成功: {EMBEDDING_MODEL}")
        except Exception as e:
            print(f"❌ 嵌入模型初始化失败: {str(e)}")
            raise
    
    def load_document(self, file_path: str) -> List[Document]:
        """
        加载单个文档
        
        Args:
            file_path: 文档路径
            
        Returns:
            Document对象列表
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        # 根据文件类型选择加载器
        suffix = file_path.suffix.lower()
        
        if suffix == ".pdf":
            loader = PyPDFLoader(str(file_path))
            documents = loader.load()
            print(f"✅ PDF文档加载成功: {file_path.name} ({len(documents)}页)")
            
        elif suffix == ".docx":
            loader = Docx2txtLoader(str(file_path))
            documents = loader.load()
            print(f"✅ DOCX文档加载成功: {file_path.name}")
            
        elif suffix == ".doc":
            # 对于.doc文件，尝试使用docx2txt
            try:
                loader = Docx2txtLoader(str(file_path))
                documents = loader.load()
                print(f"✅ DOC文档加载成功: {file_path.name}")
            except Exception as e:
                print(f"⚠️ DOC文件加载失败，建议转换为DOCX格式: {str(e)}")
                documents = []
                
        else:
            print(f"⚠️ 不支持的文件格式: {suffix}")
            documents = []
        
        # 为每个文档添加元数据
        for doc in documents:
            doc.metadata["source"] = file_path.name
            doc.metadata["file_path"] = str(file_path)
        
        return documents
    
    def load_documents_from_directory(self, directory: str) -> List[Document]:
        """
        批量加载目录中的所有文档
        
        Args:
            directory: 文档目录路径
            
        Returns:
            所有文档的Document对象列表
        """
        directory = Path(directory)
        
        if not directory.exists():
            print(f"⚠️ 目录不存在: {directory}")
            return []
        
        all_documents = []
        supported_extensions = [".pdf", ".docx", ".doc"]
        
        # 遍历目录中的所有文件
        for file_path in directory.iterdir():
            if file_path.is_file() and file_path.suffix.lower() in supported_extensions:
                try:
                    documents = self.load_document(str(file_path))
                    all_documents.extend(documents)
                except Exception as e:
                    print(f"⚠️ 加载文件失败 {file_path.name}: {str(e)}")
        
        print(f"\n📊 文档加载统计:")
        print(f"   总文档数: {len(all_documents)}")
        
        return all_documents
    
    def split_documents(self, documents: List[Document]) -> List[Document]:
        """
        对文档进行分块
        
        Args:
            documents: 原始文档列表
            
        Returns:
            分块后的文档列表
        """
        if not documents:
            print("⚠️ 没有文档需要分块")
            return []
        
        chunks = self.text_splitter.split_documents(documents)
        
        print(f"\n📊 文本分块统计:")
        print(f"   原始文档数: {len(documents)}")
        print(f"   分块大小: {CHUNK_SIZE}")
        print(f"   分块重叠: {CHUNK_OVERLAP}")
        print(f"   生成文本块数: {len(chunks)}")
        
        return chunks
    
    def build_vectorstore(self, chunks: List[Document]) -> bool:
        """
        构建向量数据库
        
        Args:
            chunks: 分块后的文档列表
            
        Returns:
            是否成功构建
        """
        if not chunks:
            print("⚠️ 没有文本块需要向量化")
            return False
        
        try:
            print(f"\n🔄 正在构建向量数据库...")
            print(f"   使用嵌入模型: {EMBEDDING_MODEL}")
            print(f"   持久化目录: {self.persist_directory}")
            
            # 创建或更新向量数据库
            self.vectorstore = Chroma.from_documents(
                documents=chunks,
                embedding=self.embeddings,
                persist_directory=self.persist_directory,
                collection_name=CHROMA_COLLECTION_NAME
            )
            
            # 获取向量库统计信息
            collection = self.vectorstore._collection
            count = collection.count()
            
            print(f"✅ 向量数据库构建成功!")
            print(f"   存储文本块数: {count}")
            
            return True
            
        except Exception as e:
            print(f"❌ 向量数据库构建失败: {str(e)}")
            return False
    
    def load_existing_vectorstore(self) -> bool:
        """
        加载已有的向量数据库
        
        Returns:
            是否成功加载
        """
        try:
            if not os.path.exists(self.persist_directory):
                print(f"⚠️ 向量数据库不存在: {self.persist_directory}")
                return False
            
            self.vectorstore = Chroma(
                persist_directory=self.persist_directory,
                embedding_function=self.embeddings,
                collection_name=CHROMA_COLLECTION_NAME
            )
            
            # 获取统计信息
            collection = self.vectorstore._collection
            count = collection.count()
            
            print(f"✅ 已加载向量数据库")
            print(f"   存储文本块数: {count}")
            
            return count > 0
            
        except Exception as e:
            print(f"❌ 加载向量数据库失败: {str(e)}")
            return False
    
    def add_documents_to_vectorstore(self, new_chunks: List[Document]) -> bool:
        """
        向现有向量库添加新文档
        
        Args:
            new_chunks: 新的分块文档
            
        Returns:
            是否成功添加
        """
        if not new_chunks:
            return False
        
        try:
            # 如果向量库不存在，先创建
            if self.vectorstore is None:
                return self.build_vectorstore(new_chunks)
            
            # 添加新文档
            self.vectorstore.add_documents(new_chunks)
            
            # 获取更新后的统计
            collection = self.vectorstore._collection
            count = collection.count()
            
            print(f"✅ 新文档已添加到向量库")
            print(f"   新增文本块数: {len(new_chunks)}")
            print(f"   当前总文本块数: {count}")
            
            return True
            
        except Exception as e:
            print(f"❌ 添加文档失败: {str(e)}")
            return False
    
    def retrieve(self, query: str, k: int = RETRIEVER_K) -> List[Document]:
        """
        检索相关文档
        
        Args:
            query: 查询文本
            k: 返回的文档数量
            
        Returns:
            最相关的k个文档块
        """
        if self.vectorstore is None:
            print("⚠️ 向量数据库未初始化")
            return []
        
        try:
            # 使用相似性搜索
            results = self.vectorstore.similarity_search(query, k=k)
            
            print(f"\n🔍 检索结果:")
            print(f"   查询: {query[:50]}...")
            print(f"   返回文档数: {len(results)}")
            
            for i, doc in enumerate(results):
                source = doc.metadata.get("source", "未知")
                content_preview = doc.page_content[:100].replace("\n", " ")
                print(f"   [{i+1}] 来源: {source}")
                print(f"       内容预览: {content_preview}...")
            
            return results
            
        except Exception as e:
            print(f"❌ 检索失败: {str(e)}")
            return []
    
    def get_retriever(self, k: int = RETRIEVER_K):
        """
        获取检索器对象（用于LangChain链）
        
        Args:
            k: 返回的文档数量
            
        Returns:
            VectorStoreRetriever对象
        """
        if self.vectorstore is None:
            raise ValueError("向量数据库未初始化")
        
        return self.vectorstore.as_retriever(search_kwargs={"k": k})
    
    def get_stats(self) -> dict:
        """
        获取知识库统计信息
        
        Returns:
            统计信息字典
        """
        stats = {
            "initialized": self.vectorstore is not None,
            "embedding_model": EMBEDDING_MODEL,
            "chunk_size": CHUNK_SIZE,
            "chunk_overlap": CHUNK_OVERLAP,
            "persist_directory": self.persist_directory
        }
        
        if self.vectorstore is not None:
            try:
                collection = self.vectorstore._collection
                stats["total_chunks"] = collection.count()
            except:
                stats["total_chunks"] = 0
        
        return stats
    
    def clear_vectorstore(self) -> bool:
        """
        清空向量数据库
        
        Returns:
            是否成功清空
        """
        try:
            if self.vectorstore is not None:
                # 删除collection
                self.vectorstore.delete_collection()
                self.vectorstore = None
            
            # 删除持久化目录
            if os.path.exists(self.persist_directory):
                import shutil
                shutil.rmtree(self.persist_directory)
            
            print("✅ 向量数据库已清空")
            return True
            
        except Exception as e:
            print(f"❌ 清空向量数据库失败: {str(e)}")
            return False


def build_knowledge_base_from_directory(directory: str) -> KnowledgeBase:
    """
    从目录构建知识库的便捷函数
    
    Args:
        directory: 文档目录路径
        
    Returns:
        KnowledgeBase对象
    """
    kb = KnowledgeBase()
    
    # 加载文档
    documents = kb.load_documents_from_directory(directory)
    
    if not documents:
        print("⚠️ 未找到任何文档")
        return kb
    
    # 分块
    chunks = kb.split_documents(documents)
    
    # 构建向量库
    kb.build_vectorstore(chunks)
    
    return kb


# 测试代码
if __name__ == "__main__":
    print("=" * 60)
    print("    知识库构建模块测试")
    print("=" * 60)
    
    # 测试文档目录
    test_dir = "./documents"
    
    if not os.path.exists(test_dir):
        print(f"⚠️ 测试目录不存在: {test_dir}")
        print("   请创建documents目录并放入PDF或DOCX文档")
        sys.exit(1)
    
    # 构建知识库
    kb = build_knowledge_base_from_directory(test_dir)
    
    # 测试检索
    print("\n" + "=" * 60)
    print("    检索功能测试")
    print("=" * 60)
    
    test_queries = [
        "什么是自然语言处理？",
        "NLP有哪些主要应用？",
        "什么是词向量？"
    ]
    
    for query in test_queries:
        results = kb.retrieve(query)
        print("\n" + "-" * 40)