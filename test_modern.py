#!/usr/bin/env python3
# privata/test_modern.py

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.enhanced_doc_loader import enhanced_loader
from utils.enhanced_chunker import semantic_chunker
from utils.structured_extractor import structured_extractor
from retriever.multi_modal_embedder import multi_modal_embedder
from retriever.reranker import reranker

def test_enhanced_loader():
    """Test the enhanced document loader"""
    print("Testing Enhanced Document Loader...")
    
    # Create a test HTML content
    test_html = """
    <html>
    <head><title>Test Mission Document</title></head>
    <body>
        <h1>INSAT-3DR Mission</h1>
        <p>Launch date: 2023-09-15</p>
        <table>
            <tr><th>Parameter</th><th>Value</th></tr>
            <tr><td>Orbit</td><td>Geostationary</td></tr>
            <tr><td>Payload</td><td>Imager and Sounder</td></tr>
        </table>
    </body>
    </html>
    """
    
    # Write test file
    test_file = "test_document.html"
    with open(test_file, 'w') as f:
        f.write(test_html)
    
    try:
        # Test loading
        docs = enhanced_loader.load_documents(test_file)
        print(f"✓ Loaded {len(docs)} documents")
        
        # Check metadata extraction
        if docs and hasattr(docs[0], 'metadata'):
            metadata = docs[0].metadata
            print(f"✓ Metadata extracted: {len(metadata)} fields")
            print(f"  Title: {metadata.get('title', 'N/A')}")
            print(f"  Tables: {metadata.get('tables_count', 0)}")
            
        return True
        
    except Exception as e:
        print(f"✗ Enhanced loader test failed: {e}")
        return False
    finally:
        # Clean up
        if os.path.exists(test_file):
            os.remove(test_file)

def test_structured_extractor():
    """Test the structured data extractor"""
    print("\nTesting Structured Data Extractor...")
    
    test_content = """
    INSAT-3DR Mission Overview
    Launch Date: September 15, 2023
    Orbit: Geostationary
    Instruments: Imager, Sounder
    
    Mission Objectives:
    1. Weather monitoring
    2. Disaster management support
    3. Oceanographic studies
    
    Key Parameters:
    Mass: 2100 kg
    Power: 2.5 kW
    Design Life: 7 years
    """
    
    try:
        result = structured_extractor.extract_structured_data(test_content)
        print(f"✓ Structured data extracted successfully")
        print(f"  Missions: {result['mission_info']['missions']}")
        print(f"  Dates: {len(result['dates'])} dates found")
        print(f"  Key-Value pairs: {len(result['key_value_pairs'])}")
        
        return True
        
    except Exception as e:
        print(f"✗ Structured extractor test failed: {e}")
        return False

def test_multi_modal_embedder():
    """Test the multi-modal embedder"""
    print("\nTesting Multi-Modal Embedder...")
    
    try:
        # Test content embedding
        content = "INSAT-3DR is a meteorological satellite"
        embedding = multi_modal_embedder.embed_content(content, "content")
        print(f"✓ Content embedding generated: {len(embedding)} dimensions")
        
        # Test title embedding
        title = "INSAT-3DR Mission"
        title_embedding = multi_modal_embedder.embed_content(title, "title")
        print(f"✓ Title embedding generated: {len(title_embedding)} dimensions")
        
        # Test similarity calculation
        similarity = multi_modal_embedder.calculate_similarity(embedding, title_embedding)
        print(f"✓ Similarity calculated: {similarity:.3f}")
        
        return True
        
    except Exception as e:
        print(f"✗ Multi-modal embedder test failed: {e}")
        return False

def test_reranker():
    """Test the reranker"""
    print("\nTesting Reranker...")
    
    try:
        # Create test embeddings
        embedder = multi_modal_embedder
        query_embedding = embedder.embed_content("weather satellite", "content")
        
        # Create test results
        test_results = [
            {"content": "INSAT-3DR weather satellite", "embedding": embedder.embed_content("INSAT-3DR weather satellite", "content")},
            {"content": "Meteorological mission overview", "embedding": embedder.embed_content("Meteorological mission overview", "content")},
            {"content": "Space technology development", "embedding": embedder.embed_content("Space technology development", "content")},
        ]
        
        # Test MMR reranking
        reranked = reranker.mmr_rerank(query_embedding, test_results)
        print(f"✓ MMR reranking completed: {len(reranked)} results")
        
        # Test duplicate removal
        duplicates_removed = reranker.remove_duplicates(test_results + test_results[:1])
        print(f"✓ Duplicate removal: {len(duplicates_removed)} unique results")
        
        return True
        
    except Exception as e:
        print(f"✗ Reranker test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("Running Modern Component Tests...")
    print("=" * 50)
    
    tests = [
        test_enhanced_loader,
        test_structured_extractor,
        test_multi_modal_embedder,
        test_reranker
    ]
    
    results = []
    for test in tests:
        try:
            results.append(test())
        except Exception as e:
            print(f"✗ Test {test.__name__} crashed: {e}")
            results.append(False)
    
    passed = sum(results)
    total = len(results)
    
    print("\n" + "=" * 50)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✓ All modern components are working correctly!")
        return 0
    else:
        print("✗ Some components need attention")
        return 1

if __name__ == "__main__":
    sys.exit(main())
