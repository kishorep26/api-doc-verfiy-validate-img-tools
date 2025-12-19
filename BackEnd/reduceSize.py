import os
from io import BytesIO
from PIL import Image

def reduce_storage(image_bytes):
    """
    Reduce image file size while maintaining quality
    Returns: reduced image bytes or None
    """
    try:
        # Open image
        img = Image.open(BytesIO(image_bytes))
        
        # Convert to RGB if necessary (for PNG with transparency)
        if img.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
            img = background
        
        # Try different quality levels to reduce size
        original_size = len(image_bytes)
        best_result = image_bytes
        
        for quality in [85, 75, 65, 55, 45]:
            output = BytesIO()
            img.save(output, format='JPEG', quality=quality, optimize=True)
            reduced_bytes = output.getvalue()
            
            # If we achieved significant reduction, use this
            if len(reduced_bytes) < original_size * 0.7:  # 30% reduction
                best_result = reduced_bytes
                break
            elif len(reduced_bytes) < len(best_result):
                best_result = reduced_bytes
        
        return best_result if len(best_result) < original_size else image_bytes
        
    except Exception as e:
        print(f"Error in reduce_storage: {e}")
        import traceback
        traceback.print_exc()
        return None