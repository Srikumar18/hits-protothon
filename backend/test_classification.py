#!/usr/bin/env python3

import json
from extract import process_pdf

def test_header_classification():
    print("Testing XGBoost Header Classification...")
    
    # Process the PDF
    result = process_pdf('Sample Heading Structure.pdf')
    
    print(f"[OK] Successfully processed {len(result['pages'])} pages")
    
    # Count classifications
    h1_count = h2_count = h3_count = body_count = 0
    
    for page in result['pages']:
        for block in page['text_blocks']:
            if block.get('level_label') == 'H1':
                h1_count += 1
            elif block.get('level_label') == 'H2':
                h2_count += 1
            elif block.get('level_label') == 'H3':
                h3_count += 1
            elif block.get('level_label') == 'BODY':
                body_count += 1
    
    print(f"[OK] Classification results:")
    print(f"  - H1 headers: {h1_count}")
    print(f"  - H2 headers: {h2_count}")
    print(f"  - H3 headers: {h3_count}")
    print(f"  - Body text: {body_count}")
    
    # Show sample classifications
    print(f"\n[OK] Sample classifications:")
    sample_count = 0
    for page in result['pages']:
        for block in page['text_blocks']:
            if sample_count >= 10:
                break
            level = block.get('level_label', 'UNKNOWN')
            text = block['text'][:60] + "..." if len(block['text']) > 60 else block['text']
            confidence = block.get('level_confidence', 0)
            print(f"  [{level}] ({confidence:.2f}): {text}")
            sample_count += 1
        if sample_count >= 10:
            break
    
    # Check structure
    structure = result.get('structure', {})
    print(f"\n[OK] Document structure has {len(structure.get('children', []))} top-level sections")
    
    print("\n[OK] XGBoost header classification test completed successfully!")
    return result

if __name__ == "__main__":
    test_header_classification()