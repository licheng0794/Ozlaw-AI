import os
from pathlib import Path
from dotenv import load_dotenv
from chromadb import Client
from langchain_community.embeddings import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from PyPDF2 import PdfReader
from bs4 import BeautifulSoup
from striprtf.striprtf import rtf_to_text

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

DATA_DIR = Path("./data")
CHROMA_DIR = Path("./data/chroma_db")

# Utility: Extract text from PDF
def extract_text_from_pdf(pdf_path):
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text

# Utility: Extract text from HTML
def extract_text_from_html(html_path):
    with open(html_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")
        return soup.get_text()

# Utility: Extract text from RTF
def extract_text_from_rtf(rtf_path):
    with open(rtf_path, "r", encoding="utf-8") as f:
        rtf_content = f.read()
    # Convert RTF to plain text
    text = rtf_to_text(rtf_content)
    return text

# Chunk text
splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)

def process_and_store(file_path):
    if file_path.suffix.lower() == ".pdf":
        text = extract_text_from_pdf(file_path)
    elif file_path.suffix.lower() == ".html":
        text = extract_text_from_html(file_path)
    elif file_path.suffix.lower() == ".rtf":
        text = extract_text_from_rtf(file_path)
    else:
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()
    chunks = splitter.split_text(text)
    # Embedding
    embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
    vectordb = Chroma(persist_directory=str(CHROMA_DIR), embedding_function=embeddings)
    vectordb.add_texts(chunks, metadatas=[{"source": str(file_path)}]*len(chunks))
    vectordb.persist()
    print(f"Processed and stored: {file_path}")

if __name__ == "__main__":
    for file in DATA_DIR.glob("*.*"):
        if file.suffix.lower() in [".pdf", ".html", ".txt", ".rtf"]:
            process_and_store(file) 