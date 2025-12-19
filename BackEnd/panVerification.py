import re
import os
import requests
from bs4 import BeautifulSoup
import time

def pan_auth_img(image_bytes):
    """
    Validates PAN card from image using OCR
    1. Extracts text using Google Cloud Vision
    2. Verifies it's an actual PAN card (keywords check)
    3. Validates PAN number format
    4. Validates number structure
    Returns: (is_valid, pan_number, confidence_score)
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
        
        # Step 1: Verify it's an actual PAN card
        pan_keywords = [
            'INCOME TAX DEPARTMENT',
            'GOVT OF INDIA',
            'GOVERNMENT OF INDIA',
            'PERMANENT ACCOUNT NUMBER',
            'PAN',
            'आयकर विभाग',
            'भारत सरकार'
        ]
        
        keyword_matches = sum(1 for keyword in pan_keywords if keyword.upper() in full_text.upper())
        
        if keyword_matches < 2:  # Need at least 2 keywords to be confident it's a PAN card
            return False, "", 0
        
        # Step 2: Extract PAN number
        regex = r"[A-Z]{5}[0-9]{4}[A-Z]{1}"
        p = re.compile(regex)
        
        pan_number = None
        for text in texts:
            text_upper = text.strip().upper().replace(" ", "").replace("-", "")
            if len(text_upper) == 10 and re.match(regex, text_upper):
                pan_number = text_upper
                break
        
        if not pan_number:
            return False, "", 0
        
        # Step 3: Validate PAN structure
        if not _validate_pan_structure(pan_number):
            return False, pan_number, 30
        
        # Step 4: Calculate confidence
        confidence = 60  # Base confidence for valid format
        confidence += min(keyword_matches * 10, 30)  # Up to 30 for keywords
        if len(texts) > 6:  # Has sufficient text
            confidence += 10
        
        # Step 5: Try to validate with Income Tax/NSDL (best effort)
        # Note: Most PAN verification APIs require authentication
        is_valid = True  # Assume valid if passes all checks
        
        return is_valid, pan_number, min(confidence, 100)
        
    except Exception as e:
        print(f"Error in pan_auth_img: {e}")
        import traceback
        traceback.print_exc()
        return False, "", 0

def pan_auth_number(number):
    """
    Validates PAN card number format and structure
    Returns: (is_valid, pan_number, confidence_score)
    """
    try:
        clean_number = number.strip().upper().replace(" ", "").replace("-", "")
        
        # Validate format
        regex = r"^[A-Z]{5}[0-9]{4}[A-Z]{1}$"
        
        if len(clean_number) != 10 or not re.match(regex, clean_number):
            return False, "", 0
        
        # Validate PAN structure
        if not _validate_pan_structure(clean_number):
            return False, clean_number, 30
        
        # Try to validate with NSDL/Income Tax website
        # Note: This requires handling CAPTCHAs and may not work reliably
        # For production, you'd need official API access
        
        return True, clean_number, 85
        
    except Exception as e:
        print(f"Error in pan_auth_number: {e}")
        return False, "", 0

def _validate_pan_structure(pan):
    """
    Validates PAN structure according to Indian Income Tax rules
    
    PAN Structure: AAAAA9999A
    - First 3 chars: Alphabetic series (AAA to ZZZ)
    - 4th char: Type of holder
      P = Individual
      C = Company
      H = HUF (Hindu Undivided Family)
      F = Firm
      A = Association of Persons
      T = AOP (Trust)
      B = Body of Individuals
      L = Local Authority
      J = Artificial Juridical Person
      G = Government
    - 5th char: First character of PAN holder's name
    - Next 4 chars: Sequential number (0001 to 9999)
    - Last char: Alphabetic check digit
    """
    try:
        if len(pan) != 10:
            return False
        
        # Check 4th character is valid type
        valid_types = ['P', 'C', 'H', 'F', 'A', 'T', 'B', 'L', 'J', 'G']
        if pan[3] not in valid_types:
            return False
        
        # Check first 5 are letters
        if not pan[:5].isalpha():
            return False
        
        # Check middle 4 are digits
        if not pan[5:9].isdigit():
            return False
        
        # Check last is letter
        if not pan[9].isalpha():
            return False
        
        # Additional validation: 5th character should be first letter of name
        # (Can't validate without name, but structure is correct)
        
        return True
    except:
        return False

def get_pan_holder_type(pan):
    """
    Returns the type of PAN holder based on 4th character
    """
    types = {
        'P': 'Individual',
        'C': 'Company',
        'H': 'Hindu Undivided Family (HUF)',
        'F': 'Firm',
        'A': 'Association of Persons (AOP)',
        'T': 'Trust (AOP)',
        'B': 'Body of Individuals (BOI)',
        'L': 'Local Authority',
        'J': 'Artificial Juridical Person',
        'G': 'Government'
    }
    
    if len(pan) >= 4:
        return types.get(pan[3], 'Unknown')
    return 'Unknown'

def _validate_pan_with_nsdl(pan):
    """
    Attempts to validate PAN with NSDL website
    Note: This is for reference only. In production:
    1. NSDL requires CAPTCHA solving
    2. Rate limiting applies
    3. Official API access is recommended
    
    This function is disabled by default as it won't work without CAPTCHA handling
    """
    # NSDL PAN verification URL (requires CAPTCHA)
    # url = "https://tin.tin.nsdl.com/pantan/StatusTrack.html"
    
    # For production, you would need:
    # 1. CAPTCHA solving service (2captcha, Anti-Captcha, etc.)
    # 2. Proper session handling
    # 3. Rate limiting
    
    # Placeholder - would need actual implementation with CAPTCHA handling
    return False

def _validate_pan_with_income_tax(pan):
    """
    Attempts to validate PAN with Income Tax Department
    Note: Similar limitations as NSDL
    
    Official verification requires:
    1. Login to e-Filing portal
    2. Or use of official APIs (requires registration)
    """
    # Income Tax e-Filing portal
    # url = "https://www.incometax.gov.in/iec/foportal/"
    
    # Placeholder - would need authentication
    return False
