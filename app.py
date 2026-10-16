"""
app.py - Streamlit Chat UI for Lumina Direct E-Commerce Store RAG Assistant

Features:
- Streamlit chat UI using st.chat_input & st.chat_message
- Documents loaded (.txt & .xlsx) and indexed ONCE at startup via @st.cache_resource
- Powered by the cheapest & fastest Google Gemini model: gemini-3.5-flash-lite
- Top-3 chunk retrieval per query via FAISS
- Answers strictly grounded in store policies and product catalog
- Responds "I don't know" when information is not in the data
- Collapsible drawer to inspect retrieved chunks and source files
"""

import os
import streamlit as st
from dotenv import load_dotenv

# Import RAG pipeline functions
from rag import load_company_documents, build_vector_store, query_rag_pipeline

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Lumina Direct | E-Commerce AI Assistant",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern e-commerce branding
st.markdown("""
<style>
    .main-title {
        font-size: 2.2rem;
        font-weight: 700;
        color: #0D5C75;
        margin-bottom: 0.1rem;
    }
    .main-subtitle {
        font-size: 1.05rem;
        color: #4B5563;
        margin-bottom: 1.2rem;
    }
    .store-badge {
        display: inline-block;
        padding: 0.25rem 0.65rem;
        font-size: 0.8rem;
        font-weight: 600;
        border-radius: 9999px;
        background-color: #E0F2FE;
        color: #0369A1;
        margin-bottom: 0.5rem;
    }
    .stChatMessage {
        border-radius: 0.85rem;
        margin-bottom: 0.8rem;
    }
</style>
""", unsafe_allow_html=True)


# ==========================================
# CACHED VECTOR STORE INITIALIZATION
# ==========================================
@st.cache_resource(show_spinner=False)
def initialize_knowledge_base(api_key: str, provider: str = "gemini"):
    """
    Loads store documents (.txt & .xlsx) and builds FAISS vector store once.
    Streamlit caches this resource across user queries so documents are not
    re-parsed or re-embedded on every question.
    """
    txt_file = "data/company_info.txt"
    xlsx_file = "data/products.xlsx"

    # Step 1: Load documents via LangChain loaders
    docs = load_company_documents(txt_path=txt_file, xlsx_path=xlsx_file)
    if not docs:
        raise ValueError("Could not find or load store documents from data/ directory.")

    # Step 2: Chunk documents & build FAISS vector store
    vector_store, chunks = build_vector_store(
        documents=docs,
        api_key=api_key,
        provider=provider,
        chunk_size=500,
        chunk_overlap=50
    )
    
    return vector_store, docs, chunks


# ==========================================
# SIDEBAR CONTROLS & STATUS
# ==========================================
with st.sidebar:
    st.markdown("### 🛍️ Store Settings")

    # Provider Selection
    provider = st.selectbox(
        "AI Provider",
        options=["Google Gemini (Recommended)", "OpenAI"],
        index=0,
        help="Google Gemini is configured with the fastest and most cost-effective models."
    )
    is_gemini = "Gemini" in provider
    provider_key = "gemini" if is_gemini else "openai"

    # API Key Input
    if is_gemini:
        default_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY") or ""
        user_key = st.text_input(
            "Gemini API Key",
            value=default_key,
            type="password",
            help="Enter your Gemini API key (or set GEMINI_API_KEY in .env)"
        )
        model_options = ["gemini-3.5-flash-lite", "gemini-3.5-flash", "gemini-3.8-flash"]
    else:
        default_key = os.getenv("OPENAI_API_KEY") or ""
        user_key = st.text_input(
            "OpenAI API Key",
            value=default_key,
            type="password",
            help="Enter your OpenAI API key (or set OPENAI_API_KEY in .env)"
        )
        model_options = ["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo"]

    active_api_key = user_key.strip() if user_key else default_key

    # Model Selection (defaults to gemini-3.5-flash-lite: cheapest & fastest)
    selected_model = st.selectbox(
        "LLM Model",
        options=model_options,
        index=0,
        help="gemini-3.5-flash-lite offers high-throughput performance with the lowest cost."
    )

    st.markdown("---")
    st.markdown("### 📦 Store Data Sources")
    txt_exists = os.path.exists("data/company_info.txt")
    xlsx_exists = os.path.exists("data/products.xlsx")

    st.markdown(f"- **Store Policies:** `company_info.txt` {'✅' if txt_exists else '❌'}")
    st.markdown(f"- **Product Catalog:** `products.xlsx` {'✅' if xlsx_exists else '❌'}")

    st.markdown("---")
    st.markdown("### 💡 Quick Customer Questions")
    sample_queries = [
        "What is your return policy and how many days do I have?",
        "Do you offer free shipping and what is the minimum spend?",
        "What is the sale price and battery life of the LuminaSound Elite Headphones?",
        "Can I split my payment into installments using Klarna or Afterpay?",
        "What is the warranty coverage for the LuminaClean X7 Robot Vacuum?",
        "Do you sell diamond engagement rings?" # Out of catalog -> Responds "I don't know"
    ]

    selected_sample = None
    for q in sample_queries:
        if st.button(q, key=f"btn_{q[:25]}", use_container_width=True):
            selected_sample = q

    st.markdown("---")
    col_clear, col_reload = st.columns(2)
    with col_clear:
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state["messages"] = []
            st.rerun()
    with col_reload:
        if st.button("🔄 Reindex", use_container_width=True):
            st.cache_resource.clear()
            st.success("Re-indexing knowledge base...")
            st.rerun()


# ==========================================
# MAIN INTERFACE
# ==========================================
st.markdown('<div class="store-badge">🏪 Official E-Commerce Store Assistant</div>', unsafe_allow_html=True)
st.markdown('<div class="main-title">Lumina Direct Customer Assistant</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="main-subtitle">Answers customer inquiries strictly using our local store policies and product inventory catalog.</div>',
    unsafe_allow_html=True
)

# API Key Validation Guard
if not active_api_key:
    key_name = "Gemini API Key (`GEMINI_API_KEY`)" if is_gemini else "OpenAI API Key (`OPENAI_API_KEY`)"
    st.warning(f"⚠️ **{key_name} Required**\nPlease enter your API key in the sidebar or define it in your `.env` file to begin.")
    st.info("""
    **RAG Pipeline Overview:**
    1. **Data Loading**: Loads `company_info.txt` (Shipping, Returns, Warranty) and `products.xlsx` (Live Product Catalog).
    2. **Chunking & FAISS**: Splits content into ~500-char chunks and builds vector index at startup (cached).
    3. **Top-3 Retrieval**: Retrieves the 3 most relevant chunks for each customer question.
    4. **Strict Grounding**: Responds only from store data. If a product or policy is not in our data, responds **"I don't know"**.
    """)
    st.stop()

# Initialize Knowledge Base (Cached via @st.cache_resource)
try:
    with st.spinner("Indexing store policies and product catalog with Gemini embeddings (runs once at startup)..."):
        vector_store, loaded_docs, total_chunks = initialize_knowledge_base(
            api_key=active_api_key,
            provider=provider_key
        )
except Exception as e:
    st.error(f"❌ Error initializing vector store: {str(e)}")
    st.stop()

# Status Banner
c1, c2, c3 = st.columns(3)
with c1:
    st.metric("Source Documents", f"{len(loaded_docs)} (.txt + .xlsx)")
with c2:
    st.metric("Indexed Chunks", f"{len(total_chunks)} chunks (~500 chars)")
with c3:
    st.metric("Model & Retrieval", f"{selected_model} (Top-3 Chunks)")

st.divider()

# Session State for Conversation History
if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {
            "role": "assistant",
            "content": (
                "👋 Welcome to **Lumina Direct**! I am your store assistant. "
                "I can answer any questions about our shipping rates, 30-day return policy, "
                "warranty options, and product specifications or prices from our catalog. How can I help you today?"
            ),
            "chunks": []
        }
    ]

# Render Message History
for msg in st.session_state["messages"]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("chunks"):
            with st.expander("🔍 Retrieved Store Context (Top-3 Chunks)", expanded=False):
                for idx, chunk in enumerate(msg["chunks"], 1):
                    source = chunk.metadata.get("file_name", "Unknown")
                    src_type = chunk.metadata.get("source_type", "Document")
                    st.markdown(f"**Chunk {idx}** | File: `{source}` ({src_type})")
                    st.caption(chunk.page_content.strip())
                    st.divider()

# Handle User Input
user_query = st.chat_input("Ask a question about our products, shipping, returns, or warranty...")

prompt_to_process = None
if user_query:
    prompt_to_process = user_query
elif selected_sample:
    prompt_to_process = selected_sample

if prompt_to_process:
    # 1. Append & display user message
    st.session_state["messages"].append({"role": "user", "content": prompt_to_process, "chunks": []})
    with st.chat_message("user"):
        st.markdown(prompt_to_process)

    # 2. Query RAG Pipeline
    with st.chat_message("assistant"):
        with st.spinner("Searching store policies and catalog..."):
            try:
                rag_result = query_rag_pipeline(
                    question=prompt_to_process,
                    vector_store=vector_store,
                    api_key=active_api_key,
                    provider=provider_key,
                    model_name=selected_model,
                    k=3
                )
                answer = rag_result["answer"]
                retrieved_chunks = rag_result["retrieved_chunks"]

                # Render assistant answer
                st.markdown(answer)

                # Show retrieved chunks for verification & grading
                if retrieved_chunks:
                    with st.expander("🔍 Retrieved Store Context (Top-3 Chunks)", expanded=False):
                        for idx, chunk in enumerate(retrieved_chunks, 1):
                            source = chunk.metadata.get("file_name", "Unknown")
                            src_type = chunk.metadata.get("source_type", "Document")
                            st.markdown(f"**Chunk {idx}** | File: `{source}` ({src_type})")
                            st.caption(chunk.page_content.strip())
                            st.divider()

                # Save assistant response
                st.session_state["messages"].append({
                    "role": "assistant",
                    "content": answer,
                    "chunks": retrieved_chunks
                })

            except Exception as ex:
                err_text = f"⚠️ Error processing query: {str(ex)}"
                st.error(err_text)
                st.session_state["messages"].append({
                    "role": "assistant",
                    "content": err_text,
                    "chunks": []
                })
