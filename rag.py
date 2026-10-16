"""
rag.py - Retrieval-Augmented Generation (RAG) Pipeline for Lumina Direct E-Commerce Store

Features:
1. Document Loading:
   - Uses TextLoader from LangChain to load store policies (.txt)
   - Uses UnstructuredExcelLoader from LangChain to load product catalog (.xlsx)
   - Combines loaded documents before chunking
2. Chunking & Indexing:
   - RecursiveCharacterTextSplitter with chunk_size ~500, overlap ~50
   - Google Generative AI embeddings (models/gemini-embedding-001) stored in a FAISS vector store
3. Grounded Retrieval:
   - Retrieves top-3 relevant chunks per question
   - Feeds context into the fastest & cheapest Gemini model (gemini-3.5-flash-lite)
   - Strict grounding instruction: If the answer is not in the data, responds "I don't know"
"""

import os
from typing import List, Tuple, Dict, Any, Optional
from dotenv import load_dotenv

# LangChain document loaders
from langchain_community.document_loaders import TextLoader, UnstructuredExcelLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.documents import Document

# Suppress unstructured commercial notice in terminal
os.environ["UNSTRUCTURED_DISABLE_NOTICE"] = "1"

load_dotenv()


def load_company_documents(
    txt_path: str = "data/company_info.txt",
    xlsx_path: str = "data/products.xlsx"
) -> List[Document]:
    """
    Loads e-commerce store data from local .txt and .xlsx files using LangChain loaders
    and combines them into a single list of documents.
    """
    all_docs: List[Document] = []
    
    # 1. Load .txt file using TextLoader
    if os.path.exists(txt_path):
        txt_loader = TextLoader(file_path=txt_path, encoding="utf-8")
        txt_docs = txt_loader.load()
        for doc in txt_docs:
            doc.metadata["source_type"] = "Store Policies & Guidelines (.txt)"
            doc.metadata["file_name"] = os.path.basename(txt_path)
        all_docs.extend(txt_docs)
    else:
        print(f"Warning: Store policies file not found at {txt_path}")

    # 2. Load .xlsx file using UnstructuredExcelLoader
    if os.path.exists(xlsx_path):
        excel_loader = UnstructuredExcelLoader(file_path=xlsx_path, mode="elements")
        xlsx_docs = excel_loader.load()
        for doc in xlsx_docs:
            doc.metadata["source_type"] = "Product Catalog (.xlsx)"
            doc.metadata["file_name"] = os.path.basename(xlsx_path)
        all_docs.extend(xlsx_docs)
    else:
        print(f"Warning: Product catalog file not found at {xlsx_path}")

    return all_docs


def build_vector_store(
    documents: List[Document],
    api_key: str,
    provider: str = "gemini",
    chunk_size: int = 500,
    chunk_overlap: int = 50
) -> Tuple[FAISS, List[Document]]:
    """
    Chunks all documents using RecursiveCharacterTextSplitter and indexes them
    into a FAISS vector store using Gemini (or OpenAI) embeddings.
    """
    if not documents:
        raise ValueError("No documents provided to build vector store.")

    # Chunk documents
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", " ", ""]
    )
    chunks = text_splitter.split_documents(documents)

    if provider.lower() == "gemini":
        from langchain_google_genai import GoogleGenerativeAIEmbeddings
        embeddings = GoogleGenerativeAIEmbeddings(
            model="models/gemini-embedding-001",
            google_api_key=api_key
        )
    else:
        from langchain_openai import OpenAIEmbeddings
        embeddings = OpenAIEmbeddings(
            openai_api_key=api_key,
            model="text-embedding-3-small"
        )

    # Build FAISS vector store
    vector_store = FAISS.from_documents(chunks, embeddings)
    return vector_store, chunks


def _extract_text_content(content: Any) -> str:
    """Helper to extract clean string from LLM response content blocks."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        texts = []
        for item in content:
            if isinstance(item, dict) and "text" in item:
                texts.append(item["text"])
            elif isinstance(item, str):
                texts.append(item)
        return "\n".join(texts)
    return str(content)


def query_rag_pipeline(
    question: str,
    vector_store: FAISS,
    api_key: str,
    provider: str = "gemini",
    model_name: Optional[str] = None,
    k: int = 3
) -> Dict[str, Any]:
    """
    Retrieves top-k relevant chunks and passes them to the LLM.
    Strictly instructs the LLM to answer only based on the retrieved company/store data,
    and to answer 'I don't know' if the answer is not present.
    """
    # 1. Retrieve top-k chunks
    retriever = vector_store.as_retriever(search_kwargs={"k": k})
    retrieved_docs: List[Document] = retriever.invoke(question)

    # 2. Format context string
    context_text = "\n\n---\n\n".join(
        [f"[Source {i+1} | {doc.metadata.get('file_name', 'Store Document')} ({doc.metadata.get('source_type', 'Policy')}):\n{doc.page_content.strip()}"
         for i, doc in enumerate(retrieved_docs)]
    )

    # 3. Prompt template enforcing strict grounding
    system_prompt = (
        "You are Lumina Direct's official E-Commerce Customer Assistant. "
        "Answer the user's question using ONLY the provided context retrieved from the store's files (.txt store policies and .xlsx product catalog).\n\n"
        "STRICT INSTRUCTIONS:\n"
        "1. If the answer to the question cannot be determined from the provided context, you MUST say \"I don't know\". "
        "Do not make up facts, assumptions, policies, prices, or specs outside the provided context.\n"
        "2. Ground your answers strictly in the retrieved data (e.g. shipping fees, return window, product prices, stock status, specs).\n"
        "3. Keep your tone polite, helpful, and concise."
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "Retrieved Store Context:\n{context}\n\nCustomer Question:\n{question}\n\nAnswer:")
    ])

    # 4. Initialize LLM (Defaults to gemini-3.5-flash-lite: fastest & cheapest)
    if provider.lower() == "gemini":
        from langchain_google_genai import ChatGoogleGenerativeAI
        selected_model = model_name or "gemini-3.5-flash-lite"
        llm = ChatGoogleGenerativeAI(
            model=selected_model,
            google_api_key=api_key
        )
    else:
        from langchain_openai import ChatOpenAI
        selected_model = model_name or "gpt-4o-mini"
        llm = ChatOpenAI(
            model=selected_model,
            temperature=0.0,
            openai_api_key=api_key
        )

    chain = prompt | llm

    # 5. Generate answer
    response = chain.invoke({"context": context_text, "question": question})
    raw_content = response.content if hasattr(response, "content") else str(response)
    answer_text = _extract_text_content(raw_content)

    return {
        "answer": answer_text,
        "retrieved_chunks": retrieved_docs,
        "context_text": context_text
    }
