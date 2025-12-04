import re
import numpy as np
import pandas as pd
from collections import defaultdict
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import xgboost as xgb
import joblib

STOPWORDS = {"the", "of", "and", "in", "to", "a", "is", "for", "on", "with", "this", "that", "are", "be", "as", "by", "from"}

def featurize_block(block, doc_stats):
    text = block["text"].strip()
    chars = len(text)
    words = re.findall(r"\S+", text)
    word_count = len(words)
    lines = text.count("\n") + 1 if text else 0
    
    upper_ratio = sum(1 for c in text if c.isupper()) / max(1, chars)
    digits_ratio = sum(1 for c in text if c.isdigit()) / max(1, chars)
    punctuation_ratio = sum(1 for c in text if re.match(r'[^\w\s]', c)) / max(1, chars)
    avg_word_len = np.mean([len(w) for w in words]) if words else 0.0
    
    starts_with_number = bool(re.match(r'^\d+(\.\d+)*', text.strip()))
    has_numbering = bool(re.match(r'^\d+[\).\s]', text.strip()))
    ends_with_colon = text.strip().endswith(":")
    title_like = sum(1 for w in words if w.istitle()) / max(1, word_count)
    stopword_ratio = sum(1 for w in words if w.lower() in STOPWORDS) / max(1, word_count)
    short_text = 1 if word_count <= 6 else 0
    
    font_size = block.get("font_size", 10)
    rel_font = font_size / doc_stats.get("median_font", 10) if doc_stats.get("median_font", 10) > 0 else 1.0
    
    page = block.get("page", 1)
    bbox = block.get("bbox", [0, 0, 100, 20])
    top_norm = bbox[1] / doc_stats.get("page_height", 800)
    left_norm = bbox[0] / doc_stats.get("page_width", 600)
    
    return np.array([
        word_count, lines, upper_ratio, avg_word_len, digits_ratio, punctuation_ratio,
        short_text, rel_font, top_norm, left_norm, title_like, stopword_ratio,
        starts_with_number, has_numbering, ends_with_colon
    ], dtype=float)

def compute_doc_stats(blocks):
    fonts = [b.get("font_size", 10) for b in blocks if b.get("font_size")]
    median_font = float(np.median(fonts)) if fonts else 10.0
    
    # Estimate page dimensions from blocks
    max_x = max((b.get("bbox", [0, 0, 600, 0])[0] + b.get("bbox", [0, 0, 600, 0])[2]) for b in blocks)
    max_y = max((b.get("bbox", [0, 0, 0, 800])[1] + b.get("bbox", [0, 0, 0, 800])[3]) for b in blocks)
    
    return {
        "median_font": median_font,
        "page_width": max_x if max_x > 0 else 600,
        "page_height": max_y if max_y > 0 else 800
    }

def rule_based_label(block, doc_stats):
    text = block["text"].strip()
    words = re.findall(r"\S+", text)
    word_count = len(words)
    
    font_size = block.get("font_size", 10)
    rel_font = font_size / doc_stats.get("median_font", 10)
    
    # Rule-based classification: 0=H1, 1=H2, 2=H3, 3=BODY
    
    # H1: Single digit followed by space and "H1:" or just single digit with large font
    if re.match(r'^\d+\s+(H1:|[A-Z])', text) or (re.match(r'^\d+\s', text) and rel_font >= 1.3):
        return 0, 0.95  # H1
    
    # H2: Pattern like "1.1" or "H2:" 
    elif re.match(r'^\d+\.\d+\s+(H2:|[A-Z])', text) or (re.match(r'^\d+\.\d+\s', text) and rel_font >= 1.1):
        return 1, 0.9   # H2
    
    # H3: Pattern like "1.1.1" or "H3:"
    elif re.match(r'^\d+\.\d+\.\d+\s+(H3:|[A-Z])', text) or re.match(r'^\d+\.\d+\.\d+\s', text):
        return 2, 0.85  # H3
    
    # BODY: Long text or doesn't match header patterns
    elif word_count > 15 or (word_count > 5 and not re.match(r'^\d+', text)):
        return 3, 0.95  # BODY
    
    # Default fallback based on font size
    elif rel_font >= 1.2:
        return 0, 0.6   # Likely H1
    elif rel_font >= 1.1:
        return 1, 0.6   # Likely H2
    else:
        return 3, 0.5   # Default to BODY

def classify_headers_xgb(blocks):
    if not blocks:
        return []
    
    doc_stats = compute_doc_stats(blocks)
    
    # Use rule-based classification only for simplicity
    results = []
    for i, block in enumerate(blocks):
        label, conf = rule_based_label(block, doc_stats)
        
        # Default to BODY if no rule matches
        if label is None:
            label = 3
            conf = 0.5
        
        level_names = ["H1", "H2", "H3", "BODY"]
        level_name = level_names[label]
        
        results.append({
            "block_id": block.get("block_id", f"b{i}"),
            "text": block["text"],
            "level": label + 1 if label < 3 else None,
            "level_label": level_name,
            "confidence": conf,
            "type": "heading" if label < 3 else "paragraph"
        })
    
    return results