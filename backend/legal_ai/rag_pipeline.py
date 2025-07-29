import os
from dotenv import load_dotenv
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.llms import OpenAI
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Fix the ChromaDB path to be relative to the project root
CHROMA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'chroma_db'))

# Set up conversational retriever and QA chain with memory
def get_qa_chain(chat_history=None):
    """Initialize the QA chain with proper error handling"""
    try:
        # Check if OpenAI API key is available
        if not OPENAI_API_KEY:
            raise ValueError("OpenAI API key not found. Please set OPENAI_API_KEY in your .env file.")
        
        # Check if ChromaDB directory exists
        if not os.path.exists(CHROMA_DIR):
            raise FileNotFoundError(f"ChromaDB directory not found at {CHROMA_DIR}. Please ensure documents have been processed.")
        
        embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
        vectordb = Chroma(persist_directory=CHROMA_DIR, embedding_function=embeddings)
        retriever = vectordb.as_retriever()
        llm = OpenAI(openai_api_key=OPENAI_API_KEY)
        memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
        
        # Populate memory with existing chat history if provided
        if chat_history:
            for turn in chat_history:
                memory.chat_memory.add_user_message(turn['question'])
                memory.chat_memory.add_ai_message(turn['answer'])
        
        qa_chain = ConversationalRetrievalChain.from_llm(
            llm=llm,
            retriever=retriever,
            memory=memory
        )
        return qa_chain
        
    except Exception as e:
        print(f"Error initializing QA chain: {e}")
        return None

# Main function to answer a question with conversation history
def answer_question(question, history=None):
    """Answer a question using the RAG pipeline with proper error handling"""
    try:
        qa_chain = get_qa_chain(chat_history=history)
        if qa_chain is None:
            return "Sorry, I'm unable to process your question at the moment. Please check that your OpenAI API key is set and documents have been processed."
        
        result = qa_chain({"question": question})
        return result['answer'] if 'answer' in result else result['result']
        
    except Exception as e:
        print(f"Error answering question: {e}")
        return f"Sorry, I encountered an error while processing your question: {str(e)}" 