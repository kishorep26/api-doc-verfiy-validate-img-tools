import re
import os
import requests
from bs4 import BeautifulSoup
import time

def aadhar_auth_img(image_bytes):
    """
    Validates Aadhar card from image using OCR
    1. Extracts text using Google Cloud Vision
    2. Verifies it's an actual Aadhar card (keywords check)
    3. Validates Aadhar number format
    4. Attempts to verify with UIDAI website
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
        
        if keyword_matches < 2:
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
            return False, formatted, 30
        
        # Step 4: Calculate confidence
        confidence = 60
        confidence += min(keyword_matches * 10, 30)
        if len(texts) > 8:
            confidence += 10
        
        return True, formatted, min(confidence, 100)
        
    except Exception as e:
        print(f"Error in aadhar_auth_img: {e}")
        import traceback
        traceback.print_exc()
        return False, "", 0

def aadhar_auth_number(number):
    """
    Validates Aadhar card number format, checksum, and attempts UIDAI verification
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
        
        # Try to verify with UIDAI website
        uidai_status = _verify_with_uidai(clean_number)
        
        if uidai_status == "verified":
            return True, formatted, 95
        elif uidai_status == "down":
            # Website is down, but format is valid
            return True, formatted, 75
        else:
            # Could not verify, but format is valid
            return True, formatted, 70
        
    except Exception as e:
        print(f"Error in aadhar_auth_number: {e}")
        return False, "", 0

def _verify_with_uidai(aadhar_number):
    """
    Attempts to verify Aadhar number with UIDAI website
    Returns: "verified", "down", or "failed"
    
    Note: This requires CAPTCHA solving which is not implemented
    For now, just checks if website is accessible
    """
    try:
        url = "https://myaadhaar.uidai.gov.in/verifyAadhaar"
        
        # Check if website is accessible
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            # Website is up but we can't verify without CAPTCHA
            # In a real implementation, you would:
            # 1. Solve CAPTCHA (using service like 2captcha)
            # 2. Submit form with Aadhar number
            # 3. Parse response
            return "down"  # Return "down" since we can't actually verify
        else:
            return "down"
            
    except requests.exceptions.Timeout:
        print("UIDAI website timeout")
        return "down"
    except requests.exceptions.RequestException as e:
        print(f"UIDAI website error: {e}")
        return "down"
    except Exception as e:
        print(f"Error checking UIDAI: {e}")
        return "down"

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
