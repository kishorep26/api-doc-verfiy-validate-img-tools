import re
import os

def aadhar_auth_img(image_bytes):
    """
    Validates Aadhar card from image bytes using OCR
    Returns: (is_valid, aadhar_number)
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
            return False, ""
            
        texts = response.text_annotations[0].description.split("\n")
        
        # Aadhar number pattern: XXXX XXXX XXXX (12 digits)
        regex = r"[2-9]{1}[0-9]{3}\s[0-9]{4}\s[0-9]{4}"
        p = re.compile(regex)
        
        for text in texts:
            if re.search(p, text):
                return True, text.strip()
        
        return False, ""
    except Exception as e:
        print(f"Error in aadhar_auth_img: {e}")
        return False, ""

def aadhar_auth_number(number):
    """
    Validates Aadhar card number format
    Returns: (is_valid, aadhar_number)
    """
    try:
        # Remove spaces and validate
        clean_number = number.replace(" ", "")
        
        # Aadhar number should be 12 digits starting with 2-9
        if len(clean_number) == 12 and clean_number.isdigit():
            if clean_number[0] in '23456789':
                # Format with spaces
                formatted = f"{clean_number[0:4]} {clean_number[4:8]} {clean_number[8:12]}"
                return True, formatted
        
        return False, ""
    except Exception as e:
        print(f"Error in aadhar_auth_number: {e}")
        return False, ""
