import re
import os
from io import BytesIO
from PIL import Image

def resize_pan_mar(image_bytes, height, width):
    """
    Resize PAN maintaining aspect ratio
    Returns: resized image bytes or None
    """
    try:
        # Open image from bytes
        img = Image.open(BytesIO(image_bytes))
        
        # Calculate height maintaining aspect ratio
        aspect_ratio = img.height / img.width
        new_height = int(width * aspect_ratio)
        
        # Resize image
        resized = img.resize((width, new_height), Image.Resampling.LANCZOS)
        
        # Convert to bytes
        output = BytesIO()
        resized.save(output, format='JPEG', quality=95)
        resized_bytes = output.getvalue()
        
        # Validate with OCR
        if _validate_pan_ocr(resized_bytes):
            return resized_bytes
        
        return None
    except Exception as e:
        print(f"Error in resize_pan_mar: {e}")
        return None

def resize_pan_hard(image_bytes, height, width):
    """
    Hard resize PAN to exact dimensions
    Returns: resized image bytes or None
    """
    try:
        # Open image from bytes
        img = Image.open(BytesIO(image_bytes))
        
        # Resize to exact dimensions
        resized = img.resize((width, height), Image.Resampling.LANCZOS)
        
        # Convert to bytes
        output = BytesIO()
        resized.save(output, format='JPEG', quality=95)
        resized_bytes = output.getvalue()
        
        # Validate with OCR
        if _validate_pan_ocr(resized_bytes):
            return resized_bytes
        
        return None
    except Exception as e:
        print(f"Error in resize_pan_hard: {e}")
        return None

def _validate_pan_ocr(image_bytes):
    """
    Validate that PAN number is still readable after resize
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
            return False
            
        texts = response.text_annotations[0].description.split("\n")
        
        # Check if PAN number pattern exists
        regex = r"[A-Z]{5}[0-9]{4}[A-Z]{1}"
        p = re.compile(regex)
        
        for text in texts:
            text = text.strip().upper()
            if len(text) == 10 and re.search(p, text):
                return True
        
        return False
    except Exception as e:
        print(f"Error in _validate_pan_ocr: {e}")
        return False
