import re
import os
import requests
from bs4 import BeautifulSoup

def aadhar_auth_img(image_bytes):
    """
    Validates Aadhar card from image using OCR
    1. Extracts text using Google Cloud Vision
    2. Verifies it's an actual Aadhar card (keywords check)
    3. Validates Aadhar number format
    4. Optionally validates number via UIDAI (if possible)
    Returns: (is_valid, aadhar_number, confidence_score)
    """
    try:
        from google.cloud import vision
        
        # Use environment variable or fallback
        creds_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS', 'credentials.json')
        if creds_path and os.path.exists(creds_path):
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = creds_path
        
        client = vision.ImageAnnotatorClient()
        image = vision.Image(content=image_bytes)
        response = client.text_detection(image=image)
        
        if not response.text_annotations:
            return False, "", 0
            
        full_text = response.text_annotations[0].description
        texts = full_text.split("\n")
        
        # Step 1: Verify it's an actual Aadhar card
        aadhar_keywords = [
            'GOVERNMENT OF INDIA',
            'आधार',
            'AADHAAR', 
            'AADHAR',
            'UNIQUE IDENTIFICATION',
            'UIDAI',
            'UID',
            'भारत सरकार'
        ]
        
        keyword_matches = sum(1 for keyword in aadhar_keywords if keyword.upper() in full_text.upper())
        
        if keyword_matches < 2:  # Need at least 2 keywords to be confident it's an Aadhar card
            return False, "", 0
        
        # Step 2: Extract Aadhar number
        regex = r"[2-9]{1}[0-9]{3}\s*[0-9]{4}\s*[0-9]{4}"
        p = re.compile(regex)
        
        aadhar_number = None
        for text in texts:
            clean_text = text.replace(" ", "").replace("-", "")
            if re.search(p, text) or (len(clean_text) == 12 and clean_text.isdigit() and clean_text[0] in '23456789'):
                aadhar_number = text.strip()
                break
        
        if not aadhar_number:
            return False, "", 0
        
        # Format the number
        clean_num = aadhar_number.replace(" ", "").replace("-", "")
        if len(clean_num) != 12:
            return False, "", 0
            
        formatted = f"{clean_num[0:4]} {clean_num[4:8]} {clean_num[8:12]}"
        
        # Step 3: Validate checksum using Verhoeff algorithm
        if not _verhoeff_validate(clean_num):
            return False, formatted, 30  # Invalid checksum
        
        # Step 4: Calculate confidence
        confidence = 60  # Base confidence for valid format
        confidence += min(keyword_matches * 10, 30)  # Up to 30 for keywords
        if len(texts) > 8:  # Has sufficient text
            confidence += 10
        
        # Step 5: Try to validate with UIDAI (optional, may not work without CAPTCHA)
        # Note: UIDAI doesn't provide public API, so this is best-effort
        is_valid = True  # Assume valid if passes all checks
        
        return is_valid, formatted, min(confidence, 100)
        
    except Exception as e:
        print(f"Error in aadhar_auth_img: {e}")
        import traceback
        traceback.print_exc()
        return False, "", 0

def aadhar_auth_number(number):
    """
    Validates Aadhar card number format and checksum
    Returns: (is_valid, aadhar_number, confidence_score)
    """
    try:
        clean_number = number.replace(" ", "").replace("-", "")
        
        # Validate format
        if len(clean_number) != 12 or not clean_number.isdigit():
            return False, "", 0
            
        if clean_number[0] not in '23456789':
            return False, "", 0
        
        # Validate using Verhoeff algorithm
        if not _verhoeff_validate(clean_number):
            return False, "", 0
        
        formatted = f"{clean_number[0:4]} {clean_number[4:8]} {clean_number[8:12]}"
        
        # Cannot validate actual existence without UIDAI API access
        # But we can validate format and checksum
        return True, formatted, 85
        
    except Exception as e:
        print(f"Error in aadhar_auth_number: {e}")
        return False, "", 0

def _verhoeff_validate(number):
    """
    Validates Aadhar number using Verhoeff algorithm
    This is the official checksum algorithm used by UIDAI
    """
    try:
        # Verhoeff multiplication table
        d = [
            [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
            [1, 2, 3, 4, 0, 6, 7, 8, 9, 5],
            [2, 3, 4, 0, 1, 7, 8, 9, 5, 6],
            [3, 4, 0, 1, 2, 8, 9, 5, 6, 7],
            [4, 0, 1, 2, 3, 9, 5, 6, 7, 8],
            [5, 9, 8, 7, 6, 0, 4, 3, 2, 1],
            [6, 5, 9, 8, 7, 1, 0, 4, 3, 2],
            [7, 6, 5, 9, 8, 2, 1, 0, 4, 3],
            [8, 7, 6, 5, 9, 3, 2, 1, 0, 4],
            [9, 8, 7, 6, 5, 4, 3, 2, 1, 0]
        ]
        
        # Permutation table
        p = [
            [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
            [1, 5, 7, 6, 2, 8, 3, 0, 9, 4],
            [5, 8, 0, 3, 7, 9, 6, 1, 4, 2],
            [8, 9, 1, 6, 0, 4, 3, 5, 2, 7],
            [9, 4, 5, 3, 1, 2, 6, 8, 7, 0],
            [4, 2, 8, 6, 5, 7, 3, 9, 0, 1],
            [2, 7, 9, 3, 8, 0, 6, 4, 1, 5],
            [7, 0, 4, 6, 9, 1, 3, 2, 5, 8]
        ]
        
        c = 0
        reversed_number = number[::-1]
        
        for i, digit in enumerate(reversed_number):
            c = d[c][p[(i % 8)][int(digit)]]
        
        return c == 0
    except:
        return False
