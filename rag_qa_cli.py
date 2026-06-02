"""
任务3：RAG问答链集成（命令行版本）
该模块将检索器和Ollama大模型连接，实现完整的RAG问答功能

AI生成说明：本模块由AI辅助生成，使用LangChain的ConversationalRetrievalChain实现RAG问答
"""

import os
import sys
from typing import List, Dict, Optional
from langchain.schema import Document

# LangChain相关导入
from langchain_community.llms import Ollama
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate

# 导入本地模块
from knowledge_base import KnowledgeBase
from config import (
    MODEL_NAME,
    OLLAMA_BASE_URL,
    SYSTEM_PROMPT,
    RETRIEVER_K,
    DOCUMENTS_DIR
)


class RAGQASystem:
    """RAG问答系统类"""
    
    def __init__(self, knowledge_base: KnowledgeBase = None):
        """
        初始化RAG问答系统
        
        Args:
            knowledge_base: 知识库对象
        """
        self.knowledge_base = knowledge_base
        self.llm = None
        self.qa_chain = None
        self.memory = None
        self.chat_history: List[Dict] = []
        
        # 初始化LLM
        self._init_llm()
        
        # 初始化记忆
        self._init_memory()
        
    def _init_llm(self):
        """初始化Ollama大模型"""
        try:
            self.llm = Ollama(
                model=MODEL_NAME,
                base_url=OLLAMA_BASE_URL,
                temperature=0.1  # 降低温度以获得更准确的回答
            )
            print(f"✅ 大模型初始化成功: {MODEL_NAME}")
        except Exception as e:
            print(f"❌ 大模型初始化失败: {str(e)}")
            raise
    
    def _init_memory(self):
        """初始化对话记忆"""
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True,
            output_key="answer"
        )
    
    def set_knowledge_base(self, knowledge_base: KnowledgeBase):
        """
        设置知识库
        
        Args:
            knowledge_base: KnowledgeBase对象
        """
        self.knowledge_base = knowledge_base
        self._build_qa_chain()
    
    def _build_qa_chain(self):
        """构建问答链"""
        if self.knowledge_base is None or self.knowledge_base.vectorstore is None:
            print("⚠️ 知识库未初始化，无法构建问答链")
            return
        
        try:
            # 获取检索器
            retriever = self.knowledge_base.get_retriever(k=RETRIEVER_K)
            
            # 创建问答链
            self.qa_chain = ConversationalRetrievalChain.from_llm(
                llm=self.llm,
                retriever=retriever,
                memory=self.memory,
                return_source_documents=True,
                verbose=False
            )
            
            print("✅ RAG问答链构建成功")
            
        except Exception as e:
            print(f"❌ 问答链构建失败: {str(e)}")
    
    def ask(self, question: str) -> Dict:
        """
        提问并获取回答
        
        Args:
            question: 用户问题
            
        Returns:
            包含回答和源文档的字典
        """
        if self.qa_chain is None:
            return {
                "answer": "⚠️ 知识库未初始化，请先构建知识库。",
                "sources": []
            }
        
        try:
            # 调用问答链
            result = self.qa_chain({"question": question})
            
            answer = result.get("answer", "")
            sources = result.get("source_documents", [])
            
            # 记录对话历史
            self.chat_history.append({
                "question": question,
                "answer": answer,
                "sources": [doc.metadata.get("source", "未知") for doc in sources]
            })
            
            return {
                "answer": answer,
                "sources": sources
            }
            
        except Exception as e:
            return {
                "answer": f"❌ 回答生成失败: {str(e)}",
                "sources": []
            }
    
    def ask_with_context_check(self, question: str) -> Dict:
        """
        提问并进行上下文检查（确保基于文档回答）
        
        Args:
            question: 用户问题
            
        Returns:
            包含回答和源文档的字典
        """
        # 先检索相关文档
        if self.knowledge_base is None:
            return {
                "answer": "⚠️ 知识库未初始化。",
                "sources": [],
                "has_context": False
            }
        
        # 检索相关内容
        relevant_docs = self.knowledge_base.retrieve(question, k=RETRIEVER_K)
        
        if not relevant_docs:
            return {
                "answer": "文档中未找到相关答案。",
                "sources": [],
                "has_context": False
            }
        
        # 构建上下文
        context = "\n\n".join([
            f"[文档: {doc.metadata.get('source', '未知')}]\n{doc.page_content}"
            for doc in relevant_docs
        ])
        
        # 使用自定义提示词
        prompt = PromptTemplate(
            template=SYSTEM_PROMPT,
            input_variables=["context", "question"]
        )
        
        # 生成回答
        formatted_prompt = prompt.format(context=context, question=question)
        
        try:
            answer = self.llm.invoke(formatted_prompt)
            
            # 记录对话历史
            self.chat_history.append({
                "question": question,
                "answer": answer,
                "sources": [doc.metadata.get("source", "未知") for doc in relevant_docs]
            })
            
            return {
                "answer": answer,
                "sources": relevant_docs,
                "has_context": True
            }
            
        except Exception as e:
            return {
                "answer": f"❌ 回答生成失败: {str(e)}",
                "sources": [],
                "has_context": False
            }
    
    def get_chat_history(self) -> List[Dict]:
        """
        获取对话历史
        
        Returns:
            对话历史列表
        """
        return self.chat_history
    
    def clear_history(self):
        """清空对话历史"""
        self.chat_history = []
        if self.memory:
            self.memory.clear()
        print("✅ 对话历史已清空")
    
    def get_stats(self) -> Dict:
        """
        获取系统统计信息
        
        Returns:
            统计信息字典
        """
        stats = {
            "model": MODEL_NAME,
            "ollama_url": OLLAMA_BASE_URL,
            "retriever_k": RETRIEVER_K,
            "chat_history_count": len(self.chat_history),
            "qa_chain_ready": self.qa_chain is not None
        }
        
        if self.knowledge_base:
            kb_stats = self.knowledge_base.get_stats()
            stats["knowledge_base"] = kb_stats
        
        return stats


def run_interactive_session(qa_system: RAGQASystem):
    """
    运行交互式问答会话
    
    Args:
        qa_system: RAG问答系统对象
    """
    print("\n" + "=" * 60)
    print("    RAG智能问答系统 - 命令行交互模式")
    print("=" * 60)
    print("\n使用说明:")
    print("  - 输入问题进行问答")
    print("  - 输入 'history' 查看对话历史")
    print("  - 输入 'stats' 查看系统状态")
    print("  - 输入 'clear' 清空对话历史")
    print("  - 输入 'quit' 或 'exit' 退出系统")
    print("=" * 60)
    
    while True:
        try:
            # 获取用户输入
            question = input("\n请输入问题: ").strip()
            
            if not question:
                continue
            
            # 处理特殊命令
            if question.lower() in ["quit", "exit", "q"]:
                print("\n👋 感谢使用，再见！")
                break
            
            elif question.lower() == "history":
                history = qa_system.get_chat_history()
                if not history:
                    print("\n暂无对话历史")
                else:
                    print("\n" + "-" * 40)
                    print("对话历史:")
                    print("-" * 40)
                    for i, item in enumerate(history):
                        print(f"\n[{i+1}] 问: {item['question']}")
                        print(f"    答: {item['answer'][:200]}...")
                        if item['sources']:
                            print(f"    来源: {', '.join(item['sources'])}")
                continue
            
            elif question.lower() == "stats":
                stats = qa_system.get_stats()
                print("\n" + "-" * 40)
                print("系统状态:")
                print("-" * 40)
                for key, value in stats.items():
                    if isinstance(value, dict):
                        print(f"\n{key}:")
                        for k, v in value.items():
                            print(f"  {k}: {v}")
                    else:
                        print(f"{key}: {value}")
                continue
            
            elif question.lower() == "clear":
                qa_system.clear_history()
                continue
            
            # 提问并获取回答
            print("\n🔍 正在检索相关文档...")
            result = qa_system.ask_with_context_check(question)
            
            # 显示回答
            print("\n" + "-" * 40)
            print("回答:")
            print("-" * 40)
            print(result["answer"])
            
            # 显示来源
            if result["sources"]:
                print("\n" + "-" * 40)
                print("参考来源:")
                print("-" * 40)
                for i, doc in enumerate(result["sources"][:3]):
                    source = doc.metadata.get("source", "未知")
                    preview = doc.page_content[:100].replace("\n", " ")
                    print(f"[{i+1}] {source}")
                    print(f"    内容预览: {preview}...")
            
        except KeyboardInterrupt:
            print("\n\n👋 感谢使用，再见！")
            break
        except Exception as e:
            print(f"\n❌ 发生错误: {str(e)}")


def test_qa_system():
    """
    测试问答系统效果
    """
    print("\n" + "=" * 60)
    print("    RAG问答系统测试")
    print("=" * 60)
    
    # 检查文档目录
    if not os.path.exists(DOCUMENTS_DIR):
        print(f"⚠️ 文档目录不存在: {DOCUMENTS_DIR}")
        print("   请创建documents目录并放入相关文档")
        return
    
    # 构建知识库
    print("\n步骤1: 构建知识库")
    print("-" * 40)
    kb = KnowledgeBase()
    documents = kb.load_documents_from_directory(DOCUMENTS_DIR)
    
    if not documents:
        print("⚠️ 未找到任何文档，测试终止")
        return
    
    chunks = kb.split_documents(documents)
    kb.build_vectorstore(chunks)
    
    # 创建问答系统
    print("\n步骤2: 初始化问答系统")
    print("-" * 40)
    qa_system = RAGQASystem(knowledge_base=kb)
    
    # 测试问题列表
    test_questions = [
        # 与文档相关的问题（5个）
        "什么是自然语言处理？",
        "NLP有哪些主要应用领域？",
        "什么是词向量？它有什么作用？",
        "什么是Transformer模型？",
        "BERT模型的特点是什么？",
        # 与文档无关的问题（2个）
        "今天北京的天气怎么样？",
        "如何制作红烧肉？"
    ]
    
    print("\n步骤3: 测试问答效果")
    print("-" * 40)
    
    test_results = []
    
    for i, question in enumerate(test_questions):
        print(f"\n[测试 {i+1}] 问题: {question}")
        print("-" * 40)
        
        result = qa_system.ask_with_context_check(question)
        
        print(f"回答: {result['answer'][:300]}...")
        
        if result['sources']:
            sources = [doc.metadata.get('source', '未知') for doc in result['sources']]
            print(f"来源文档: {', '.join(sources)}")
        else:
            print("来源文档: 无")
        
        # 记录测试结果
        test_results.append({
            "question": question,
            "has_answer": result['has_context'],
            "sources_count": len(result['sources'])
        })
    
    # 输出测试总结
    print("\n" + "=" * 60)
    print("    测试结果总结")
    print("=" * 60)
    
    related_questions = test_results[:5]
    unrelated_questions = test_results[5:]
    
    print("\n相关问题测试:")
    for r in related_questions:
        status = "✅" if r['has_answer'] else "❌"
        print(f"  {status} {r['question'][:30]}... (来源数: {r['sources_count']})")
    
    print("\n无关问题测试:")
    for r in unrelated_questions:
        # 无关问题应该没有来源或返回"未找到"
        status = "✅ 正确拒答" if not r['has_answer'] or r['sources_count'] == 0 else "⚠️ 可能幻觉"
        print(f"  {status} {r['question'][:30]}...")
    
    print("\n" + "=" * 60)


def main():
    """主函数"""
    print("=" * 60)
    print("    RAG智能问答系统 - 命令行版本")
    print("=" * 60)
    
    # 检查文档目录
    if not os.path.exists(DOCUMENTS_DIR):
        print(f"\n⚠️ 文档目录不存在: {DOCUMENTS_DIR}")
        print("   正在创建文档目录...")
        os.makedirs(DOCUMENTS_DIR)
        print(f"   ✅ 已创建: {DOCUMENTS_DIR}")
        print("   请将PDF或DOCX文档放入该目录后重新运行")
        return
    
    # 构建知识库
    print("\n正在构建知识库...")
    kb = KnowledgeBase()
    
    # 尝试加载已有向量库
    if kb.load_existing_vectorstore():
        print("✅ 已加载现有知识库")
    else:
        # 构建新知识库
        documents = kb.load_documents_from_directory(DOCUMENTS_DIR)
        if documents:
            chunks = kb.split_documents(documents)
            kb.build_vectorstore(chunks)
        else:
            print("⚠️ 未找到文档，请将PDF或DOCX文档放入documents目录")
            return
    
    # 创建问答系统
    qa_system = RAGQASystem(knowledge_base=kb)
    
    # 运行交互会话
    run_interactive_session(qa_system)


if __name__ == "__main__":
    # 可以选择运行测试或交互模式
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        test_qa_system()
    else:
        main()