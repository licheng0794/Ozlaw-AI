import os
import sys
import tempfile
from unittest.mock import patch, MagicMock
from pathlib import Path

# Add the project root to the path
project_root = os.path.join(os.path.dirname(__file__), '..')
sys.path.insert(0, project_root)

from backend.legal_ai.rag_pipeline import get_qa_chain, answer_question

def test_rag_pipeline_without_api_key():
    """Test RAG pipeline behavior when OpenAI API key is missing"""
    
    # Temporarily remove API key
    original_key = os.environ.get('OPENAI_API_KEY')
    if 'OPENAI_API_KEY' in os.environ:
        del os.environ['OPENAI_API_KEY']
    
    try:
        # Test that the function handles missing API key gracefully
        result = answer_question("What is Australian law?")
        
        print("=== RAG Pipeline Test (No API Key) ===")
        print(f"Result: {result}")
        
        # Should return an error message
        assert "OpenAI API key" in result or "unable to process" in result
        print("✅ RAG pipeline handles missing API key correctly")
        
    finally:
        # Restore API key
        if original_key:
            os.environ['OPENAI_API_KEY'] = original_key

def test_rag_pipeline_with_mock_chain():
    """Test RAG pipeline with mocked components"""
    
    # Mock the OpenAI API key
    with patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'}):
        
        # Mock the ChromaDB and other components
        with patch('backend.legal_ai.rag_pipeline.OpenAIEmbeddings') as mock_embeddings, \
             patch('backend.legal_ai.rag_pipeline.Chroma') as mock_chroma, \
             patch('backend.legal_ai.rag_pipeline.OpenAI') as mock_llm, \
             patch('backend.legal_ai.rag_pipeline.ConversationBufferMemory') as mock_memory, \
             patch('backend.legal_ai.rag_pipeline.ConversationalRetrievalChain') as mock_chain, \
             patch('os.path.exists', return_value=True):
            
            # Set up mocks
            mock_chain_instance = MagicMock()
            mock_chain_instance.return_value = {'answer': 'This is a test response'}
            mock_chain.from_llm.return_value = mock_chain_instance
            
            # Test the function
            result = answer_question("What is Australian law?")
            
            print("=== RAG Pipeline Test (Mocked) ===")
            print(f"Result: {result}")
            
            # Should return the mocked response
            assert "test response" in result
            print("✅ RAG pipeline works with mocked components")
            
            # Verify that the chain was called
            mock_chain_instance.assert_called_once()

def test_rag_pipeline_chat_history():
    """Test RAG pipeline with chat history"""
    
    # Mock the OpenAI API key
    with patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'}):
        
        # Mock the components
        with patch('backend.legal_ai.rag_pipeline.OpenAIEmbeddings') as mock_embeddings, \
             patch('backend.legal_ai.rag_pipeline.Chroma') as mock_chroma, \
             patch('backend.legal_ai.rag_pipeline.OpenAI') as mock_llm, \
             patch('backend.legal_ai.rag_pipeline.ConversationBufferMemory') as mock_memory, \
             patch('backend.legal_ai.rag_pipeline.ConversationalRetrievalChain') as mock_chain, \
             patch('os.path.exists', return_value=True):
            
            # Set up mocks
            mock_chain_instance = MagicMock()
            mock_chain_instance.return_value = {'answer': 'This is a follow-up response'}
            mock_chain.from_llm.return_value = mock_chain_instance
            
            mock_memory_instance = MagicMock()
            mock_memory.return_value = mock_memory_instance
            
            # Test with chat history
            history = [
                {'question': 'What is the first question?', 'answer': 'First answer'},
                {'question': 'What is the second question?', 'answer': 'Second answer'}
            ]
            
            result = answer_question("What is the third question?", history=history)
            
            print("=== RAG Pipeline Test (With Chat History) ===")
            print(f"Result: {result}")
            print(f"History length: {len(history)}")
            
            # Should return the mocked response
            assert "follow-up response" in result
            print("✅ RAG pipeline works with chat history")
            
            # Verify that memory was populated with history
            assert mock_memory_instance.chat_memory.add_user_message.call_count == 2
            assert mock_memory_instance.chat_memory.add_ai_message.call_count == 2

def test_rag_pipeline_error_handling():
    """Test RAG pipeline error handling"""
    
    # Mock the OpenAI API key
    with patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'}):
        
        # Mock the components to raise an exception
        with patch('backend.legal_ai.rag_pipeline.OpenAIEmbeddings') as mock_embeddings, \
             patch('os.path.exists', return_value=True):
            
            # Make the embeddings constructor raise an exception
            mock_embeddings.side_effect = Exception("Test error")
            
            result = answer_question("What is Australian law?")
            
            print("=== RAG Pipeline Test (Error Handling) ===")
            print(f"Result: {result}")
            
            # Should return an error message
            assert "error" in result.lower()
            print("✅ RAG pipeline handles errors gracefully")

def test_chromadb_path():
    """Test that the ChromaDB path is correctly resolved"""
    
    from backend.legal_ai.rag_pipeline import CHROMA_DIR
    
    print("=== ChromaDB Path Test ===")
    print(f"ChromaDB path: {CHROMA_DIR}")
    
    # Check if the path points to the expected location
    expected_path = os.path.abspath(os.path.join(
        os.path.dirname(__file__), '..', 'data', 'chroma_db'
    ))
    
    print(f"Expected path: {expected_path}")
    print(f"Paths match: {CHROMA_DIR == expected_path}")
    
    # The paths should match
    assert CHROMA_DIR == expected_path
    print("✅ ChromaDB path is correctly resolved")

if __name__ == "__main__":
    print("Running RAG Pipeline Tests...")
    
    # Run all tests
    test_chromadb_path()
    test_rag_pipeline_without_api_key()
    test_rag_pipeline_with_mock_chain()
    test_rag_pipeline_chat_history()
    test_rag_pipeline_error_handling()
    
    print("\n🎉 All RAG pipeline tests completed!") 