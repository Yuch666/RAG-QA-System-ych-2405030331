"""
任务4：Streamlit Web界面开发
该模块实现完整的Web应用界面，包含文档上传、知识库构建、问答交互等功能

AI生成说明：本模块由AI辅助生成，使用Streamlit构建交互式Web界面
"""

import os
import sys
import time
import tempfile
from pathlib import Path
from typing import List, Dict

import streamlit as st

# 导入本地模块
from knowledge_base import KnowledgeBase
from config import (
    MODEL_NAME,
    EMBEDDING_MODEL,
    CHUNK_SIZE,
    CHUNK_OVERLAP,
    CHROMA_PERSIST_DIR,
    DOCUMENTS_DIR,
    RETRIEVER_K
)


# 页面配置
st.set_page_config(
    page_title="RAG智能问答系统",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS样式
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #424242;
        margin-top: 1rem;
    }
    .success-message {
        padding: 1rem;
        background-color: #E8F5E9;
        border-radius: 0.5rem;
        color: #2E7D32;
    }
    .warning-message {
        padding: 1rem;
        background-color: #FFF3E0;
        border-radius: 0.5rem;
        color: #EF6C00;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 0.5rem;
    }
    .user-message {
        background-color: #E3F2FD;
        border-left: 4px solid #1E88E5;
    }
    .assistant-message {
        background-color: #F5F5F5;
        border-left: 4px solid #757575;
    }
    .source-box {
        padding: 0.5rem;
        background-color: #FFF8E1;
        border-radius: 0.3rem;
        font-size: 0.9rem;
        margin-top: 0.5rem;
    }
    .stats-box {
        padding: 1rem;
        background-color: #ECEFF1;
        border-radius: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)


def init_session_state():
    """初始化会话状态"""
    # 知识库对象
    if "knowledge_base" not in st.session_state:
        st.session_state.knowledge_base = None
    
    # 对话历史
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    
    # 知识库状态
    if "kb_initialized" not in st.session_state:
        st.session_state.kb_initialized = False
    
    # 文档数量统计
    if "document_count" not in st.session_state:
        st.session_state.document_count = 0
    
    # 文本块数量统计
    if "chunk_count" not in st.session_state:
        st.session_state.chunk_count = 0
    
    # 上传的文件列表
    if "uploaded_files" not in st.session_state:
        st.session_state.uploaded_files = []
    
    # 处理状态
    if "processing" not in st.session_state:
        st.session_state.processing = False


def get_knowledge_base():
    """获取或创建知识库对象"""
    if st.session_state.knowledge_base is None:
        st.session_state.knowledge_base = KnowledgeBase()
    return st.session_state.knowledge_base


def sidebar_section():
    """侧边栏区域"""
    with st.sidebar:
        st.markdown("### 📋 系统配置")
        
        # 模型信息展示
        st.markdown("---")
        st.markdown("**当前模型配置**")
        st.info(f"对话模型: {MODEL_NAME}")
        st.info(f"嵌入模型: {EMBEDDING_MODEL}")
        
        # 参数配置展示
        st.markdown("---")
        st.markdown("**处理参数**")
        st.text(f"分块大小: {CHUNK_SIZE}")
        st.text(f"分块重叠: {CHUNK_OVERLAP}")
        st.text(f"检索数量: {RETRIEVER_K}")
        
        # 知识库状态
        st.markdown("---")
        st.markdown("### 📊 知识库状态")
        
        if st.session_state.kb_initialized:
            st.success("✅ 知识库已初始化")
            st.metric("文档数量", st.session_state.document_count)
            st.metric("文本块数量", st.session_state.chunk_count)
        else:
            st.warning("⚠️ 知识库未初始化")
            st.info("请上传文档并构建知识库")
        
        # 操作按钮
        st.markdown("---")
        st.markdown("### 🔧 操作")
        
        if st.button("🗑️ 清空知识库", type="secondary"):
            kb = get_knowledge_base()
            if kb.clear_vectorstore():
                st.session_state.kb_initialized = False
                st.session_state.document_count = 0
                st.session_state.chunk_count = 0
                st.session_state.uploaded_files = []
                st.success("知识库已清空")
                time.sleep(1)
                st.rerun()
        
        if st.button("🔄 清空对话历史", type="secondary"):
            st.session_state.chat_history = []
            st.success("对话历史已清空")
            time.sleep(1)
            st.rerun()
        
        # 使用说明
        st.markdown("---")
        st.markdown("### 📖 使用说明")
        st.markdown("""
1. 上传PDF或DOCX文档
2. 点击"构建知识库"
3. 在问答区输入问题
4. 查看回答和来源文档
        """)


def document_upload_section():
    """文档上传区域"""
    st.markdown("### 📁 文档上传")
    
    # 文件上传组件
    uploaded_files = st.file_uploader(
        "上传PDF或DOCX文档",
        type=["pdf", "docx", "doc"],
        accept_multiple_files=True,
        help="支持上传多个PDF或DOCX文档"
    )
    
    if uploaded_files:
        st.session_state.uploaded_files = uploaded_files
        st.success(f"已选择 {len(uploaded_files)} 个文件")
        
        # 显示文件列表
        with st.expander("查看已上传文件"):
            for file in uploaded_files:
                file_size = file.size / 1024  # KB
                st.text(f"📄 {file.name} ({file_size:.1f} KB)")
    
    # 构建知识库按钮
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        build_button = st.button(
            "🔨 构建知识库",
            type="primary",
            disabled=not uploaded_files or st.session_state.processing
        )
    
    with col2:
        # 添加文档按钮（增量添加）
        add_button = st.button(
            "➕ 添加到知识库",
            type="secondary",
            disabled=not uploaded_files or not st.session_state.kb_initialized or st.session_state.processing
        )
    
    # 处理上传的文件
    if build_button or add_button:
        process_uploaded_files(uploaded_files, is_add=add_button)


def process_uploaded_files(uploaded_files: List, is_add: bool = False):
    """
    处理上传的文件
    
    Args:
        uploaded_files: 上传的文件列表
        is_add: 是否为增量添加模式
    """
    st.session_state.processing = True
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    kb = get_knowledge_base()
    
    try:
        # 创建临时目录保存上传的文件
        temp_dir = tempfile.mkdtemp()
        saved_files = []
        
        # 保存上传的文件
        status_text.text("正在保存上传的文件...")
        progress_bar.progress(10)
        
        for i, file in enumerate(uploaded_files):
            file_path = os.path.join(temp_dir, file.name)
            with open(file_path, "wb") as f:
                f.write(file.getbuffer())
            saved_files.append(file_path)
            progress_bar.progress(10 + (i + 1) * 10 / len(uploaded_files))
        
        # 加载文档
        status_text.text("正在加载文档...")
        progress_bar.progress(30)
        
        all_documents = []
        for file_path in saved_files:
            documents = kb.load_document(file_path)
            all_documents.extend(documents)
        
        progress_bar.progress(50)
        
        if not all_documents:
            st.error("未能加载任何文档内容")
            return
        
        # 文本分块
        status_text.text("正在分块处理...")
        progress_bar.progress(60)
        
        chunks = kb.split_documents(all_documents)
        
        progress_bar.progress(70)
        
        # 向量化存储
        status_text.text("正在构建向量数据库...")
        progress_bar.progress(80)
        
        if is_add:
            # 增量添加
            success = kb.add_documents_to_vectorstore(chunks)
        else:
            # 新建知识库
            success = kb.build_vectorstore(chunks)
        
        progress_bar.progress(90)
        
        if success:
            # 更新状态
            st.session_state.kb_initialized = True
            
            # 获取统计信息
            stats = kb.get_stats()
            st.session_state.chunk_count = stats.get("total_chunks", len(chunks))
            
            # 计算文档数量（去重）
            sources = set()
            for doc in all_documents:
                sources.add(doc.metadata.get("source", "未知"))
            st.session_state.document_count = len(sources)
            
            status_text.text("处理完成！")
            progress_bar.progress(100)
            
            st.success(f"✅ 知识库构建成功！")
            st.info(f"文档数量: {st.session_state.document_count} | 文本块数量: {st.session_state.chunk_count}")
            
            time.sleep(1)
            st.rerun()
        else:
            st.error("知识库构建失败")
        
    except Exception as e:
        st.error(f"处理过程中出错: {str(e)}")
    
    finally:
        st.session_state.processing = False
        progress_bar.empty()
        status_text.empty()
        
        # 清理临时文件
        try:
            import shutil
            shutil.rmtree(temp_dir)
        except:
            pass


def qa_interaction_section():
    """问答交互区域"""
    st.markdown("### 💬 问答交互")
    
    # 检查知识库状态
    if not st.session_state.kb_initialized:
        st.warning("⚠️ 请先上传文档并构建知识库")
        return
    
    # 问题输入框
    question = st.text_input(
        "输入您的问题",
        placeholder="例如：什么是自然语言处理？",
        key="question_input"
    )
    
    # 提问按钮
    col1, col2, col3 = st.columns([1, 1, 3])
    
    with col1:
        ask_button = st.button(
            "🔍 提问",
            type="primary",
            disabled=not question
        )
    
    # 处理提问
    if ask_button and question:
        process_question(question)


def process_question(question: str):
    """
    处理用户提问
    
    Args:
        question: 用户问题
    """
    kb = get_knowledge_base()
    
    # 显示处理状态
    with st.spinner("正在检索和生成回答..."):
        try:
            # 检索相关文档
            relevant_docs = kb.retrieve(question, k=RETRIEVER_K)
            
            if not relevant_docs:
                answer = "文档中未找到相关答案。"
                sources = []
            else:
                # 构建上下文
                context = "\n\n".join([
                    f"[文档: {doc.metadata.get('source', '未知')}]\n{doc.page_content}"
                    for doc in relevant_docs
                ])
                
                # 使用Ollama生成回答
                from langchain_community.llms import Ollama
                from config import OLLAMA_BASE_URL, SYSTEM_PROMPT
                from langchain.prompts import PromptTemplate
                
                llm = Ollama(model=MODEL_NAME, base_url=OLLAMA_BASE_URL)
                
                prompt = PromptTemplate(
                    template=SYSTEM_PROMPT,
                    input_variables=["context", "question"]
                )
                
                formatted_prompt = prompt.format(context=context, question=question)
                answer = llm.invoke(formatted_prompt)
                
                sources = relevant_docs
            
            # 记录对话历史
            st.session_state.chat_history.append({
                "question": question,
                "answer": answer,
                "sources": sources,
                "timestamp": time.strftime("%H:%M:%S")
            })
            
        except Exception as e:
            st.error(f"回答生成失败: {str(e)}")
            return
    
    # 清空输入框
    st.session_state.question_input = ""


def chat_history_section():
    """对话历史展示区域"""
    st.markdown("### 📜 对话历史")
    
    if not st.session_state.chat_history:
        st.info("暂无对话记录")
        return
    
    # 显示最近的对话记录
    history_count = len(st.session_state.chat_history)
    st.caption(f"共 {history_count} 条对话记录")
    
    # 反向显示（最新的在最上面）
    for item in reversed(st.session_state.chat_history):
        # 用户问题
        st.markdown(f"""
<div class="chat-message user-message">
    <strong>👤 用户 ({item.get('timestamp', '')}):</strong><br>
    {item['question']}
</div>
        """, unsafe_allow_html=True)
        
        # 系统回答
        st.markdown(f"""
<div class="chat-message assistant-message">
    <strong>🤖 系统:</strong><br>
    {item['answer']}
</div>
        """, unsafe_allow_html=True)
        
        # 来源文档
        if item['sources']:
            with st.expander("📚 参考来源"):
                for i, doc in enumerate(item['sources'][:3]):
                    source = doc.metadata.get('source', '未知')
                    preview = doc.page_content[:200].replace("\n", " ")
                    st.markdown(f"""
<div class="source-box">
    <strong>[{i+1}] {source}</strong><br>
    {preview}...
</div>
                    """, unsafe_allow_html=True)
        
        st.markdown("---")


def knowledge_base_status_section():
    """知识库状态展示区域"""
    st.markdown("### 📊 知识库详情")
    
    kb = get_knowledge_base()
    
    if st.session_state.kb_initialized:
        stats = kb.get_stats()
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("文本块总数", stats.get("total_chunks", 0))
        
        with col2:
            st.metric("分块大小", stats.get("chunk_size", CHUNK_SIZE))
        
        with col3:
            st.metric("分块重叠", stats.get("chunk_overlap", CHUNK_OVERLAP))
        
        # 显示详细信息
        with st.expander("查看详细配置"):
            st.json({
                "嵌入模型": stats.get("embedding_model", EMBEDDING_MODEL),
                "持久化目录": stats.get("persist_directory", CHROMA_PERSIST_DIR),
                "初始化状态": stats.get("initialized", False)
            })
    else:
        st.info("知识库尚未初始化")


def main():
    """主函数"""
    # 初始化会话状态
    init_session_state()
    
    # 页面标题
    st.markdown("<h1 class='main-header'>📚 RAG智能问答系统</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #757575;'>基于本地知识库的检索增强生成问答系统</p>", unsafe_allow_html=True)
    
    # 侧边栏
    sidebar_section()
    
    # 主内容区域
    st.markdown("---")
    
    # 创建标签页
    tab1, tab2, tab3 = st.tabs(["📁 文档管理", "💬 问答交互", "📊 知识库状态"])
    
    with tab1:
        # 文档上传区域
        document_upload_section()
        
        # 显示已上传文件列表
        if st.session_state.uploaded_files:
            st.markdown("---")
            st.markdown("#### 已上传的文件")
            for file in st.session_state.uploaded_files:
                st.text(f"📄 {file.name}")
    
    with tab2:
        # 问答交互区域
        qa_interaction_section()
        
        st.markdown("---")
        
        # 对话历史
        chat_history_section()
    
    with tab3:
        # 知识库状态
        knowledge_base_status_section()
        
        # 显示统计信息
        if st.session_state.kb_initialized:
            st.markdown("---")
            st.markdown("#### 系统信息")
            st.info(f"""
- **对话模型**: {MODEL_NAME}
- **嵌入模型**: {EMBEDDING_MODEL}
- **Ollama地址**: http://localhost:11434
- **检索数量**: {RETRIEVER_K}
            """)


if __name__ == "__main__":
    main()