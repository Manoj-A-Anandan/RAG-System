import os
from dotenv import load_dotenv
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import MarkdownTextSplitter
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

# Setup Vector Store (Persistent) - Note: New embeddings will require re-indexing if DB exists
PERSIST_DIRECTORY = "./db"

def get_vector_store():
    if not os.path.exists("./data/portfolio_data.md"):
        print("Warning: Portfolio data not found.")
        return None

    # Load Data
    loader = TextLoader("./data/portfolio_data.md")
    documents = loader.load()

    # Split Data (Better for Markdown)
    text_splitter = MarkdownTextSplitter(chunk_size=1000, chunk_overlap=200)
    texts = text_splitter.split_documents(documents)

    # Embeddings - Local (Free, Unlimited)
    print("Initializing HuggingFace Embeddings (Local)...")
    from langchain_huggingface import HuggingFaceEmbeddings
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    # Create/Load Vector Store
    try:
        from langchain_community.vectorstores import Chroma
        
        # Check if running in a cloud environment (like Render) where filesystem might be ephemeral/readonly
        # or simply force InMemory for simpler maintenance on free tiers
        is_cloud = os.getenv("RENDER") or os.getenv("RAILWAY_ENVIRONMENT")
        
        if is_cloud:
             raise ImportError("Force InMemory for Cloud")

        # Simple Logic: If we are initializing, just overwrite to ensure fresh data
        # In a real app, you'd check hashes. Here, we force fresh for the user.
        vectordb = Chroma.from_documents(
            documents=texts, 
            embedding=embeddings,
            persist_directory=PERSIST_DIRECTORY
        )
        print("Initialized (and Refreshed) ChromaDB VectorStore")
    except Exception as e:
        print(f"ChromaDB skipped/failed ({e}), using InMemoryVectorStore")
        from langchain_core.vectorstores import InMemoryVectorStore
        vectordb = InMemoryVectorStore.from_documents(
            documents=texts,
            embedding=embeddings
        )
    return vectordb

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

def get_qa_chain():
    vectordb = get_vector_store()
    if not vectordb:
        return None
        
    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key:
        print("Error: GROQ_API_KEY missing.")
        return None
        
    # Free, Fast, High Limits
    # Using llama-3.3-70b-versatile as llama3-8b-8192 is deprecated
    llm = ChatGroq(model="llama-3.3-70b-versatile", groq_api_key=groq_api_key, temperature=0.3)

    retriever = vectordb.as_retriever(search_kwargs={"k": 3})
    
    prompt_template = """Use the following pieces of context from the portfolio to answer the question at the end. 
    If you don't know the answer, just say that you don't know, don't try to make up an answer.
    Keep the answer concise and professional, as if you are the assistant of the portfolio owner.

    Context: {context}

    Question: {question}
    Answer:"""
    
    prompt = PromptTemplate(
        template=prompt_template, input_variables=["context", "question"]
    )

    # LCEL Chain
    rag_chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    
    return rag_chain
