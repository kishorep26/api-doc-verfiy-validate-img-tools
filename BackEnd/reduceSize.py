import os
from io import BytesIO
from PIL import Image

def reduce_storage(image_bytes):
    """
    Reduce image file size while maintaining readability
    Returns: reduced image bytes or None
    """
    try:
        from google.cloud import vision
        
        # Use environment variable or fallback
        creds_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS', 'credentials.json')
        if creds_path and os.path.exists(creds_path):
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = creds_path
        
        client = vision.ImageAnnotatorClient()
        
        # Get original text
        original_image = vision.Image(content=image_bytes)
        original_response = client.text_detection(image=original_image)
        
        if not original_response.text_annotations:
            return None
            
        original_texts = set(original_response.text_annotations[0].description.split("\n"))
        
        # Open image
        img = Image.open(BytesIO(image_bytes))
        
        # Try different quality levels
        for quality in range(10, 100, 10):
            output = BytesIO()
            img.save(output, format='JPEG', quality=quality, optimize=True)
            reduced_bytes = output.getvalue()
            
            # Validate text is still readable
            reduced_image = vision.Image(content=reduced_bytes)
            reduced_response = client.text_detection(image=reduced_image)
            
            if not reduced_response.text_annotations:
                continue
                
            reduced_texts = set(reduced_response.text_annotations[0].description.split("\n"))
            
            # Check if at least 90% of text is preserved
            common_texts = original_texts.intersection(reduced_texts)
            if len(common_texts) / len(original_texts) > 0.9:
                return reduced_bytes
        
        # If no suitable quality found, return original
        return image_bytes
        
    except Exception as e:
        print(f"Error in reduce_storage: {e}")
        return None