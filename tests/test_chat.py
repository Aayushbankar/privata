#!/usr/bin/env python3
"""
Test script to debug the chat system
"""

import os
import sys

# Set up environment
os.environ["GEMINI_API_KEY"] = "AIzaSyA22BG94hYIO6y79U7nuZDd73Nbeu3CEeA"
os.environ["LLM_MODE"] = "api"

def test_llm():
    """Test LLM functionality"""
    print("🔍 Testing LLM...")
    try:
        import sys
        sys.path.append('src/models')
        from llm_loader import get_llm_info, run_llm
        info = get_llm_info()
        print(f"✅ LLM Info: {info}")
        
        # Test simple LLM call
        response = run_llm("Hello, can you say 'test successful'?")
        print(f"✅ LLM Response: {response}")
        return True
    except Exception as e:
        print(f"❌ LLM Error: {e}")
        return False

def test_vector_db():
    """Test vector database"""
    print("\n🔍 Testing Vector Database...")
    try:
        import sys
        sys.path.append('src/retrieval')
        from modern_vectordb import vector_db
        stats = vector_db.get_collection_stats()
        print(f"✅ Vector DB Stats: {stats}")
        return True
    except Exception as e:
        print(f"❌ Vector DB Error: {e}")
        return False

def test_embedder():
    """Test embedder"""
    print("\n🔍 Testing Embedder...")
    try:
        import sys
        sys.path.append('src/retrieval')
        from multi_modal_embedder import multi_modal_embedder
        test_query = "What is MOSDAC?"
        embedding = multi_modal_embedder.embed_query(test_query)
        print(f"✅ Embedding generated, length: {len(embedding)}")
        return True
    except Exception as e:
        print(f"❌ Embedder Error: {e}")
        return False

def test_retrieval():
    """Test retrieval system"""
    print("\n🔍 Testing Retrieval...")
    try:
        import sys
        sys.path.append('src/retrieval')
        from modern_vectordb import vector_db
        import sys
        sys.path.append('src/retrieval')
        from multi_modal_embedder import multi_modal_embedder
        
        query = "What is MOSDAC?"
        query_embedding = multi_modal_embedder.embed_query(query)
        results = vector_db.query_similar_docs(query_embedding, top_k=5)
        print(f"✅ Retrieved {len(results)} documents")
        if results:
            print(f"   First result: {results[0].get('content', '')[:100]}...")
        return True
    except Exception as e:
        print(f"❌ Retrieval Error: {e}")
        return False

def test_chat_system():
    """Test chat system"""
    print("\n🔍 Testing Chat System...")
    try:
        import sys
        sys.path.append('src/chat')
        from chat import ModernChatSystem
        
        chat = ModernChatSystem()
        query = "What is MOSDAC?"
        
        # Test retrieval
        results = chat.retrieve_relevant_docs(query)
        print(f"✅ Retrieved {len(results)} documents")
        
        if results:
            # Test context formatting
            context = chat.format_context_with_citations(results)
            print(f"✅ Context formatted, length: {len(context)}")
            
            # Test response generation
            response = chat.generate_response(query, context, False)
            print(f"✅ Response generated: {response[:200]}...")
        else:
            print("❌ No documents retrieved")
            
        return True
    except Exception as e:
        print(f"❌ Chat System Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("🧪 Testing MOSDAC Chat System Components")
    print("=" * 50)
    
    tests = [
        ("LLM", test_llm),
        ("Vector DB", test_vector_db),
        ("Embedder", test_embedder),
        ("Retrieval", test_retrieval),
        ("Chat System", test_chat_system)
    ]
    
    results = {}
    for name, test_func in tests:
        results[name] = test_func()
    
    print("\n📊 Test Results:")
    print("=" * 20)
    for name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{name}: {status}")
    
    all_passed = all(results.values())
    print(f"\nOverall: {'✅ ALL TESTS PASSED' if all_passed else '❌ SOME TESTS FAILED'}")

if __name__ == "__main__":
    main()
