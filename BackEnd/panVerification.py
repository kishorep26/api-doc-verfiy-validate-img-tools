import re
import os

def pan_auth_img(image_bytes):
    """
    Validates PAN card from image bytes using OCR
    Returns: (is_valid, pan_number)
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
        
        # PAN card pattern: AAAAA9999A (5 letters, 4 digits, 1 letter)
        regex = r"[A-Z]{5}[0-9]{4}[A-Z]{1}"
        p = re.compile(regex)
        
        for text in texts:
            text = text.strip().upper()
            if len(text) == 10 and re.search(p, text):
                return True, text
        
        return False, ""
    except Exception as e:
        print(f"Error in pan_auth_img: {e}")
        return False, ""

def pan_auth_number(number):
    """
    Validates PAN card number format
    Returns: (is_valid, pan_number)
    """
    try:
        # Clean and uppercase
        clean_number = number.strip().upper()
        
        # PAN should be 10 characters: 5 letters, 4 digits, 1 letter
        regex = r"^[A-Z]{5}[0-9]{4}[A-Z]{1}$"
        
        if len(clean_number) == 10 and re.match(regex, clean_number):
            return True, clean_number
        
        return False, ""
    except Exception as e:
        print(f"Error in pan_auth_number: {e}")
        return False, ""
