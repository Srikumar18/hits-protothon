import os
import datetime
import re
import json
import statistics
from collections import Counter
import pdfplumber
import camelot
import fitz  # PyMuPDF
import pytesseract
from pdf2image import convert_from_path
import numpy as np
import cv2
from xgb_classifier import classify_blocks_with_split
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer, WordNetLemmatizer
from nltk.tag import pos_tag
import string
from summarizer import summarize_text, extractive_summarize

# Download required NLTK data (run once)
try:
    nltk.data.find('tokenizers/punkt_tab')
except LookupError:
    nltk.download('punkt_tab')
    
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')
    
try:
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('wordnet')
    
try:
    nltk.data.find('taggers/averaged_perceptron_tagger_eng')
except LookupError:
    nltk.download('averaged_perceptron_tagger_eng')

def get_timestamp():
    return datetime.datetime.now().isoformat()

def extract_keywords_advanced(text, max_keywords=8):
    """
    Advanced keyword extraction with proper NLP preprocessing:
    1. Tokenization: Split text into words/tokens
    2. Normalization: Convert to lowercase, remove punctuation
    3. Stop-word Removal: Remove common words
    4. Stemming/Lemmatization: Reduce words to root form
    5. POS filtering: Keep only meaningful parts of speech
    """
    if not text or len(text.strip()) < 10:
        return []
    
    # Step 1: Tokenization - Split text into words
    try:
        tokens = word_tokenize(text.lower())
    except LookupError:
        # Fallback to simple tokenization if NLTK data is not available
        tokens = re.findall(r'\b\w+\b', text.lower())
    
    # Step 2: Normalization - Remove punctuation and non-alphabetic tokens
    # Keep only alphabetic tokens with length > 2
    normalized_tokens = [
        token for token in tokens 
        if token.isalpha() and len(token) > 2
    ]
    
    # Step 3: Stop-word Removal - Remove common English words
    stop_words = set(stopwords.words('english'))
    # Add extensive custom stop words for better filtering
    custom_stop_words = {
        'said', 'say', 'get', 'go', 'know', 'make', 'see', 'come', 'could', 
        'would', 'also', 'one', 'two', 'first', 'last', 'way', 'use', 'used',
        'using', 'may', 'might', 'must', 'shall', 'will', 'can', 'cannot',
        'example', 'examples', 'figure', 'table', 'page', 'section', 'chapter',
        'please', 'thank', 'thanks', 'regards', 'sincerely', 'dear', 'sir', 'madam',
        'information', 'details', 'contact', 'phone', 'email', 'address', 'website',
        'free', 'toll', 'hours', 'time', 'date', 'number', 'code', 'reference',
        'supply', 'supplier', 'provide', 'service', 'services', 'company', 'limited',
        'india', 'indian', 'delhi', 'mumbai', 'bangalore', 'chennai', 'kolkata',
        'new', 'old', 'good', 'bad', 'best', 'better', 'great', 'excellent',
        'available', 'booking', 'book', 'reserved', 'confirm', 'confirmation'
    }
    stop_words.update(custom_stop_words)
    
    filtered_tokens = [token for token in normalized_tokens if token not in stop_words]
    
    # Step 4: POS Tagging - Keep only nouns, adjectives, and verbs
    pos_tagged = pos_tag(filtered_tokens)
    meaningful_tokens = [
        word for word, pos in pos_tagged 
        if pos.startswith(('NN', 'JJ', 'VB'))  # Nouns, Adjectives, Verbs
    ]
    
    # Step 5: Lemmatization - Reduce words to their root form
    lemmatizer = WordNetLemmatizer()
    
    def get_wordnet_pos(treebank_tag):
        """Convert treebank POS tag to wordnet POS tag"""
        if treebank_tag.startswith('J'):
            return 'a'  # adjective
        elif treebank_tag.startswith('V'):
            return 'v'  # verb
        elif treebank_tag.startswith('N'):
            return 'n'  # noun
        elif treebank_tag.startswith('R'):
            return 'r'  # adverb
        else:
            return 'n'  # default to noun
    
    # Re-tag the meaningful tokens for lemmatization
    meaningful_pos_tagged = pos_tag(meaningful_tokens)
    lemmatized_tokens = [
        lemmatizer.lemmatize(word, get_wordnet_pos(pos))
        for word, pos in meaningful_pos_tagged
    ]
    
    # Step 6: Frequency Analysis and Keyword Selection
    # Count frequency of lemmatized tokens
    word_freq = Counter(lemmatized_tokens)
    
    # More strict filtering for meaningful keywords
    min_freq = max(2, len(lemmatized_tokens) // 50)  # At least 2% frequency
    max_freq = len(lemmatized_tokens) // 8   # Not more than 12.5% frequency
    
    # Domain-specific meaningful words (keep these even if frequent)
    domain_keywords = {
        'railway', 'train', 'passenger', 'ticket', 'booking', 'reservation',
        'departure', 'arrival', 'platform', 'station', 'journey', 'travel',
        'refund', 'cancellation', 'insurance', 'policy', 'premium', 'coverage',
        'microprocessor', 'processor', 'memory', 'register', 'instruction',
        'algorithm', 'database', 'network', 'security', 'encryption', 'protocol'
    }
    
    filtered_keywords = {}
    for word, freq in word_freq.items():
        if len(word) >= 5:
            # Keep domain keywords regardless of frequency
            if word.lower() in domain_keywords:
                filtered_keywords[word] = freq
            # Keep other words only if they meet frequency criteria
            elif min_freq <= freq <= max_freq:
                filtered_keywords[word] = freq
    
    # Step 7: Score keywords based on frequency and length
    scored_keywords = {
        word: freq * (len(word) / 10)  # Slight preference for longer words
        for word, freq in filtered_keywords.items()
    }
    
    # Step 8: Extract top keywords
    top_keywords = sorted(scored_keywords.items(), key=lambda x: x[1], reverse=True)
    
    # Return top keywords (word only, not frequency) with better filtering
    final_keywords = []
    for word, score in top_keywords[:max_keywords * 2]:  # Get more candidates
        if len(word) >= 5 and word.isalpha():  # Only alphabetic words
            # Skip generic terms
            generic_terms = {'please', 'supply', 'information', 'details', 'service'}
            if word.lower() not in generic_terms:
                final_keywords.append(word)
        if len(final_keywords) >= max_keywords:
            break
    
    return final_keywords

def extract_technical_terms(text, max_terms=4):
    """
    Extract only meaningful technical terms and acronyms
    """
    technical_terms = []
    
    # Find meaningful acronyms (3-5 uppercase letters, avoid common words)
    acronyms = re.findall(r'\b[A-Z]{3,5}\b', text)
    # Filter out common non-technical acronyms
    excluded_acronyms = {'THE', 'AND', 'FOR', 'YOU', 'ARE', 'NOT', 'BUT', 'CAN', 'ALL', 'NEW', 'OLD'}
    meaningful_acronyms = [a for a in acronyms if a not in excluded_acronyms]
    technical_terms.extend(meaningful_acronyms)
    
    # Find technical patterns (words with numbers)
    tech_patterns = re.findall(r'\b[A-Za-z]+[0-9]+[A-Za-z0-9]*\b', text)
    technical_terms.extend(tech_patterns)
    
    # Find specific technical/business terms (proper nouns that are likely meaningful)
    # Look for sequences of capitalized words that are likely company/product names
    proper_nouns = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3}\b', text)
    
    # Filter to keep only likely technical/business terms
    meaningful_terms = []
    for term in proper_nouns:
        # Skip common sentence starters and generic terms
        if not any(term.startswith(x) for x in ['The ', 'This ', 'That ', 'These ', 'Please ', 'Thank ']):
            # Keep terms that look like company names, product names, or technical terms
            if len(term.split()) <= 3 and len(term) >= 6:  # Not too long, not too short
                meaningful_terms.append(term)
    
    technical_terms.extend(meaningful_terms)
    
    # Remove duplicates and return only the most relevant ones
    unique_terms = list(dict.fromkeys(technical_terms))  # Preserve order
    # Return only top terms, prioritizing shorter, more specific ones
    filtered_terms = [term for term in unique_terms if 5 <= len(term) <= 25]
    return filtered_terms[:max_terms]

def clean_text(text):
    if not text:
        return ""
    return re.sub(r'\s+', ' ', text).strip()

def normalize_bbox(bbox, page_height):
    # pdfplumber: (x0, top, x1, bottom)
    # Target: [x, y, w, h]
    x0, top, x1, bottom = bbox
    return [round(x0, 2), round(top, 2), round(x1 - x0, 2), round(bottom - top, 2)]

def get_font_stats(words):
    if not words:
        return 0, 0
    sizes = [w.get('size', 10) for w in words]
    return statistics.mean(sizes), max(sizes)

def classify_block(text, font_size, avg_font_size, is_bold):
    # Placeholder - will be replaced by XGBoost classification
    return "paragraph"

def cluster_words_into_blocks(words, page_width, page_height):
    """
    Cluster words into blocks based on vertical and horizontal proximity.
    """
    if not words:
        return []

    # Sort by vertical position (top), then horizontal (x0)
    words.sort(key=lambda w: (w['top'], w['x0']))

    blocks = []
    current_block = [words[0]]
    
    # Thresholds
    line_height_threshold = 10  # Max difference in 'top' to be considered same line
    block_gap_threshold = 20    # Max vertical gap to be considered same block

    for w in words[1:]:
        prev = current_block[-1]
        
        # Check if same line
        vertical_diff = abs(w['top'] - prev['top'])
        horizontal_diff = w['x0'] - prev['x1']
        
        # Check if same block (vertical gap not too large)
        # We also check if the horizontal gap is reasonable for the same line
        
        is_same_line = vertical_diff < 5
        is_next_line = (w['top'] - prev['bottom']) < block_gap_threshold
        
        if is_same_line or is_next_line:
            current_block.append(w)
        else:
            # Finalize current block
            blocks.append(current_block)
            current_block = [w]
            
    blocks.append(current_block)

    # Convert word clusters to block dicts
    result_blocks = []
    
    # Calculate global average font size for classification
    all_sizes = [w.get('size', 10) for w in words]
    global_avg_size = statistics.mean(all_sizes) if all_sizes else 10

    for i, cluster in enumerate(blocks):
        # Bounding box of cluster
        x0 = min(w['x0'] for w in cluster)
        top = min(w['top'] for w in cluster)
        x1 = max(w['x1'] for w in cluster)
        bottom = max(w['bottom'] for w in cluster)
        
        text = " ".join([w['text'] for w in cluster])
        
        # Avg font size of block
        block_sizes = [w.get('size', 10) for w in cluster]
        avg_size = statistics.mean(block_sizes)
        max_size = max(block_sizes)
        
        # Check for bold (pdfplumber 'non_stroking_color' or fontname often indicates bold)
        # Simplified: assume larger font is heading
        
        block_type = classify_block(text, avg_size, global_avg_size, False)
        
        result_blocks.append({
            "block_id": f"p{{page}}_b{i+1}", # Placeholder, will format later
            "text": text,
            "bbox": [round(x0, 2), round(top, 2), round(x1 - x0, 2), round(bottom - top, 2)],
            "type": block_type,
            "ocr_confidence": 0.99, # Digital PDF
            "font_size": avg_size, # Internal use
            "page": None  # Will be set later
        })
        
    return result_blocks

def extract_structure(classified_blocks):
    """
    Build hierarchical structure from XGBoost classified blocks.
    """
    root = {
        "id": "root_1",
        "type": "document",
        "text": "",
        "level": 0,
        "page_refs": [],
        "confidence": 1.0,
        "children": []
    }
    
    current_h1 = None
    current_h2 = None
    
    for block in classified_blocks:
        node = {
            "id": f"n{len(root['children']) + 1}",
            "type": block['type'],
            "text": block['text'],
            "level": block.get('level', 4),
            "page_refs": [{"page": 1, "block_id": block['block_id']}],
            "confidence": block['confidence']
        }
        
        if block['level_label'] == 'H1':
            if current_h1:
                root['children'].append(current_h1)
            current_h1 = node
            current_h1['children'] = []
            current_h2 = None
            if not root['text']:
                root['text'] = block['text']
        elif block['level_label'] == 'H2':
            if current_h2:
                if current_h1:
                    current_h1['children'].append(current_h2)
                else:
                    root['children'].append(current_h2)
            current_h2 = node
            current_h2['children'] = []
        elif block['level_label'] == 'H3':
            if current_h2:
                current_h2['children'].append(node)
            elif current_h1:
                current_h1['children'].append(node)
            else:
                root['children'].append(node)
        else:  # BODY
            if current_h2:
                current_h2['children'].append(node)
            elif current_h1:
                current_h1['children'].append(node)
            else:
                root['children'].append(node)
    
    # Add remaining sections
    if current_h2 and current_h1:
        current_h1['children'].append(current_h2)
    if current_h1:
        root['children'].append(current_h1)
        
    return root

def process_pdf(pdf_path):
    # Metadata
    metadata = {
        "total_pages": 0,
        "total_images": 0,
        "total_tables": 0,
        "ocr_engine": "Tesseract",
        "ocr_version": "5.3.0",
        "avg_ocr_confidence": 0.0,
        "generated_at": get_timestamp()
    }
    
    pages_output = []
    all_blocks_flat = []
    total_confidence = 0
    block_count = 0
    
    # Open PDF with pdfplumber
    with pdfplumber.open(pdf_path) as pdf:
        metadata["total_pages"] = len(pdf.pages)
        
        for i, page in enumerate(pdf.pages):
            page_num = i + 1
            width = page.width
            height = page.height
            
            page_data = {
                "page": page_num,
                "width": float(width),
                "height": float(height),
                "text_blocks": [],
                "tables": [],
                "images": [],
                "images_count": 0
            }
            
            # 1. Extract Text Blocks (Digital)
            words = page.extract_words(extra_attrs=['fontname', 'size'])
            
            # If no words found, try OCR (Scanned PDF)
            if not words:
                # Convert to image
                # Note: This requires poppler installed and in path
                try:
                    images = convert_from_path(pdf_path, first_page=page_num, last_page=page_num)
                    if images:
                        img = images[0]
                        # Run Tesseract with error handling
                        try:
                            ocr_data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
                        except Exception as tesseract_error:
                            print(f"Tesseract OCR failed for page {page_num}: {tesseract_error}")
                            # Fallback: create minimal text block indicating OCR failure
                            page_data["text_blocks"].append({
                                "block_id": f"p{page_num}_b1",
                                "text": "[OCR processing failed - image-based content detected]",
                                "bbox": [0, 0, width, height],
                                "type": "paragraph",
                                "ocr_confidence": 0.0
                            })
                            continue
                        # Raw OCR text removed to reduce bloat
                        
                        # Convert OCR data to blocks
                        n_boxes = len(ocr_data['text'])
                        current_ocr_block = None
                        
                        for j in range(n_boxes):
                            if int(ocr_data['conf'][j]) > 0:
                                txt = ocr_data['text'][j].strip()
                                if not txt: continue
                                
                                x, y, w, h = ocr_data['left'][j], ocr_data['top'][j], ocr_data['width'][j], ocr_data['height'][j]
                                conf = float(ocr_data['conf'][j]) / 100.0
                                
                                # Simple block merging could be done here, but for now let's just make words/lines
                                # Ideally we group by 'block_num' or 'par_num' from tesseract
                                
                                # Using tesseract's block_num/par_num/line_num
                                blk_id = f"p{page_num}_b{ocr_data['block_num'][j]}"
                                
                                # Check if we already have this block
                                existing = next((b for b in page_data["text_blocks"] if b["block_id"] == blk_id), None)
                                if existing:
                                    existing["text"] += " " + txt
                                    # Update bbox to encompass new word
                                    # bbox: [x, y, w, h]
                                    ex, ey, ew, eh = existing["bbox"]
                                    ex1 = ex + ew
                                    ey1 = ey + eh
                                    nx1 = x + w
                                    ny1 = y + h
                                    
                                    final_x = min(ex, x)
                                    final_y = min(ey, y)
                                    final_w = max(ex1, nx1) - final_x
                                    final_h = max(ey1, ny1) - final_y
                                    
                                    existing["bbox"] = [final_x, final_y, final_w, final_h]
                                    existing["ocr_confidence"] = (existing["ocr_confidence"] + conf) / 2
                                else:
                                    page_data["text_blocks"].append({
                                        "block_id": blk_id,
                                        "text": txt,
                                        "bbox": [x, y, w, h],
                                        "type": "paragraph", # Default
                                        "ocr_confidence": conf
                                    })
                except Exception as e:
                    print(f"OCR Failed for page {page_num}: {e}")
            else:
                # Digital PDF
                blocks = cluster_words_into_blocks(words, width, height)
                full_text = []
                for idx, b in enumerate(blocks):
                    b["block_id"] = f"p{page_num}_b{idx+1}"
                    b["page"] = page_num # For structure builder
                    
                    # Track for structure
                    all_blocks_flat.append(b)
                    
                    total_confidence += b["ocr_confidence"]
                    block_count += 1
                    
                # Raw OCR text removed to reduce bloat

            # 2. Extract Tables (Camelot) - Only lattice for bordered tables
            try:
                # Only use lattice flavor for tables with clear borders
                tables = camelot.read_pdf(pdf_path, pages=str(page_num), flavor='lattice')
                
                valid_tables = 0
                for t_idx, table in enumerate(tables):
                    # Very strict filtering for real tables
                    confidence = table.accuracy / 100.0
                    if confidence < 0.8:  # Only high-confidence tables
                        continue
                        
                    df = table.df
                    rows = df.values.tolist()
                    
                    # Must have at least 2 rows and 2 columns for a real table
                    if len(rows) < 2 or (rows and len(rows[0]) < 2):
                        continue
                    
                    # Check for proper table structure - multiple columns with data
                    cols_with_data = 0
                    for col_idx in range(len(rows[0]) if rows else 0):
                        col_has_data = any(str(rows[row_idx][col_idx]).strip() for row_idx in range(len(rows)))
                        if col_has_data:
                            cols_with_data += 1
                    
                    if cols_with_data < 2:  # Must have at least 2 columns with data
                        continue
                    
                    # Skip if it's mostly single-column content (likely text, not table)
                    non_empty_cells = sum(1 for row in rows for cell in row if str(cell).strip())
                    total_cells = len(rows) * len(rows[0]) if rows else 0
                    if total_cells == 0 or non_empty_cells / total_cells < 0.3:  # At least 30% filled
                        continue
                    
                    headers = rows[0] if rows else []
                    
                    # BBox conversion
                    c_bbox = table._bbox
                    t_x = c_bbox[0]
                    t_y = height - c_bbox[3]
                    t_w = c_bbox[2] - c_bbox[0]
                    t_h = c_bbox[3] - c_bbox[1]
                    
                    page_data["tables"].append({
                        "table_id": f"t{metadata['total_tables'] + valid_tables + 1}",
                        "bbox": [round(t_x, 2), round(t_y, 2), round(t_w, 2), round(t_h, 2)],
                        "rows": rows,
                        "headers": headers,
                        "extracted_by": "camelot",
                        "confidence": confidence
                    })
                    valid_tables += 1
                
                metadata["total_tables"] += valid_tables
            except Exception as e:
                print(f"Table extraction failed: {e}")

            # 3. Extract Images (PyMuPDF)
            try:
                # Extract filename without extension
                base_file_name = os.path.splitext(os.path.basename(pdf_path))[0]
                base_file_name = base_file_name.replace(" ", "_")  # Optional: clean spaces

                doc = fitz.open(pdf_path)
                f_page = doc[i]
                image_list = f_page.get_images(full=True)

                for img_index, img in enumerate(image_list):
                    xref = img[0]

                    pix = fitz.Pixmap(doc, xref)

                    # NEW: Filename now includes original PDF name
                    img_name = f"{base_file_name}_page_{page_num}_img_{img_index}.png"
                    img_path = os.path.join("extracted_images", img_name)

                    os.makedirs("extracted_images", exist_ok=True)

                    # Save the image
                    if pix.n < 5:
                        pix.save(img_path)
                    else:
                        pix1 = fitz.Pixmap(fitz.csRGB, pix)
                        pix1.save(img_path)
                        pix1 = None

                    pix = None

                    # Update your API return paths
                    page_data["images"].append(f"/images/{img_name}")
                    metadata["total_images"] += 1
                    page_data["images_count"] += 1

                doc.close()

            except Exception as e:
                print(f"Image extraction failed: {e}")


            pages_output.append(page_data)

    # Calculate global metadata
    if block_count > 0:
        metadata["avg_ocr_confidence"] = round(total_confidence / block_count, 2)
    
    # Classify headers using XGBoost
    classified_blocks = classify_blocks_with_split(all_blocks_flat)
    
    # Update pages with classified blocks
    block_idx = 0
    for page_data in pages_output:
        page_blocks = []
        while block_idx < len(classified_blocks) and classified_blocks[block_idx]['block_id'].startswith(f"p{page_data['page']}_"):
            block = classified_blocks[block_idx]
            # Convert to page format - KEEP ALL CLASSIFICATION DATA
            orig_block = all_blocks_flat[block_idx]
            page_blocks.append({
                "block_id": block['block_id'],
                "text": block['text'],
                "bbox": orig_block['bbox'],
                "type": block['type'],
                "ocr_confidence": orig_block['ocr_confidence'],
                "level_label": block['level_label'],
                "level_confidence": block['confidence'],
                "level": block.get('level')
            })
            block_idx += 1
        page_data["text_blocks"] = page_blocks
    
    # Build Structure
    structure = extract_structure(classified_blocks)
    
    # Advanced Keywords Extraction
    all_text = " ".join([" ".join([b["text"] for b in p["text_blocks"]]) for p in pages_output])
    
    # Extract only NLP-based keywords (no technical terms)
    keywords = extract_keywords_advanced(all_text, max_keywords=10)
    
    # Use the distilled summarizer to produce the auto_summary
    try:
        auto_summary = summarize_text(all_text, max_chunk_chars=1200, min_length=50, max_length=200)
        #auto_summary = extractive_summarize(all_text, max_sentences=5)
        # Clean up whitespace/newlines
        auto_summary = re.sub(r'\s+', ' ', auto_summary).strip()
    except Exception as e:
        # Fallback: short excerpt (never fail)
        auto_summary = (all_text[:500] + "...") if len(all_text) > 500 else all_text
    
    summary = {
        "auto_summary": auto_summary,
        "keywords": keywords
    }
    
    # Evaluation (Mock)
    evaluation = {
        "run_id": f"eval_{datetime.datetime.now().strftime('%Y_%m_%d_%H%M')}",
        "heading_f1": 0.95,
        "parent_child_f1": 0.90,
        "normalized_ted": 0.92,
        "semantic_sim_mean": 0.93,
        "notes": "Automated extraction"
    }
    
    # Provenance
    provenance = {
        "steps": [
            {"step": "pdf_extract", "tool": "pdfplumber_v0.10", "ts": get_timestamp()},
            {"step": "table_extract", "tool": "camelot_v0.11", "ts": get_timestamp()},
            {"step": "structure_build", "tool": "heuristic_v1", "ts": get_timestamp()}
        ]
    }

    # Entities (Simple Regex/Keyword based)
    entities = []
    tech_keywords = ["8086", "8255", "Mode 0", "PPI", "Microprocessor", "Microcontroller"]
    for page in pages_output:
        for block in page["text_blocks"]:
            for kw in tech_keywords:
                if kw in block["text"]:
                    entities.append({
                        "text": kw,
                        "type": "TECH",
                        "page_refs": [{"page": page["page"], "block_id": block["block_id"]}],
                        "confidence": 0.9
                    })
    # Deduplicate entities
    unique_entities = []
    seen_entities = set()
    for e in entities:
        key = (e["text"], e["page_refs"][0]["page"])
        if key not in seen_entities:
            seen_entities.add(key)
            unique_entities.append(e)

    # Filter out empty arrays
    tables = [t for p in pages_output for t in p.get("tables", [])]
    
    result = {
        "file": os.path.basename(pdf_path),
        "metadata": metadata,
        "pages": pages_output,
        "structure": structure,
        "summary": summary,
        "evaluation": evaluation,
        "provenance": provenance
    }
    
    # Only include non-empty arrays
    if tables:
        result["tables"] = tables
    if unique_entities:
        result["entities"] = unique_entities
        
    return result