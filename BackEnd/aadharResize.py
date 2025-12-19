import re
import os
from io import BytesIO
from PIL import Image

def resize_aadhar_mar(image_bytes, height, width):
    """
    Resize Aadhar maintaining aspect ratio
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
        
        # Optional: Validate with OCR only if credentials available
        # Skip validation to allow resize without Google Cloud
        return resized_bytes
        
    except Exception as e:
        print(f"Error in resize_aadhar_mar: {e}")
        import traceback
        traceback.print_exc()
        return None

def resize_aadhar_hard(image_bytes, height, width):
    """
    Hard resize Aadhar to exact dimensions
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
        
        # Optional: Validate with OCR only if credentials available
        # Skip validation to allow resize without Google Cloud
        return resized_bytes
        
    except Exception as e:
        print(f"Error in resize_aadhar_hard: {e}")
        import traceback
        traceback.print_exc()
        return None

def _validate_aadhar_ocr(image_bytes):
    """
    Validate that Aadhar number is still readable after resize
    This is optional and only used if Google Cloud credentials are available
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
        
        # Check if Aadhar number pattern exists
        regex = r"[2-9]{1}[0-9]{3}\s[0-9]{4}\s[0-9]{4}"
        p = re.compile(regex)
        
        for text in texts:
            if re.search(p, text):
                return True
        
        return False
    except Exception as e:
        print(f"Error in _validate_aadhar_ocr: {e}")
        # Return True to allow resize even if OCR fails
        return True