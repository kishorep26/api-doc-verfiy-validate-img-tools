import re
import sys
import os
import json
from io import BytesIO

# Add BackEnd directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'BackEnd'))

from flask import Flask, render_template, Response, request, send_file, jsonify
from werkzeug.utils import secure_filename
from PIL import Image

# Import backend modules
try:
    import aadharVerification
    import panVerification
    import panResize 
    import aadharResize
    import reduceSize
except ImportError as e:
    print(f"Warning: Could not import backend modules: {e}")

app = Flask(__name__, 
            template_folder='Frontend/Templates',
            static_folder='Frontend/static')

app.config['UPLOAD_FOLDER'] = "/tmp/images"
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/aadhar")
def aadhar_page():
    return render_template("aadhar.html")

@app.route("/pan")
def pan_page():
    return render_template("pan.html")

@app.route("/resize")
def resize_page():
    return render_template("resize.html")


@app.route("/aadharVerification", methods=['POST', 'GET'])
def aadhar():
    try:
        if request.files and 'file' in request.files:   
            if request.files['file'].filename != "":
                file_bytes = request.files['file'].read()
                is_valid, num, confidence = aadharVerification.aadhar_auth_img(file_bytes)
                return jsonify({
                    'valid': bool(is_valid),
                    'number': str(num),
                    'confidence': int(confidence),
                    'message': 'Aadhar card verified successfully' if is_valid else 'Invalid or unreadable Aadhar card'
                })
        else:
            number = request.form.get("number", "")
            is_valid, num, confidence = aadharVerification.aadhar_auth_number(number)
            return jsonify({
                'valid': bool(is_valid),
                'number': str(num),
                'confidence': int(confidence),
                'message': 'Valid Aadhar number' if is_valid else 'Invalid Aadhar number format'
            })
    except Exception as e:
        print(f"Error in aadhar verification: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'valid': False,
            'number': '',
            'confidence': 0,
            'error': str(e),
            'message': 'Error processing Aadhar verification'
        }), 403

@app.route("/panVerification", methods=['POST', 'GET'])
def pan():
    try:
        if request.files and 'file' in request.files:   
            if request.files['file'].filename != "":
                file_bytes = request.files['file'].read()
                is_valid, num, confidence = panVerification.pan_auth_img(file_bytes)
                holder_type = panVerification.get_pan_holder_type(num) if num else ''
                return jsonify({
                    'valid': bool(is_valid),
                    'number': str(num),
                    'confidence': int(confidence),
                    'holder_type': holder_type,
                    'message': 'PAN card verified successfully' if is_valid else 'Invalid or unreadable PAN card'
                })
        else:
            number = request.form.get("number", "")
            is_valid, num, confidence = panVerification.pan_auth_number(number)
            holder_type = panVerification.get_pan_holder_type(num) if num else ''
            return jsonify({
                'valid': bool(is_valid),
                'number': str(num),
                'confidence': int(confidence),
                'holder_type': holder_type,
                'message': 'Valid PAN number' if is_valid else 'Invalid PAN number format'
            })
    except Exception as e:
        print(f"Error in PAN verification: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'valid': False,
            'number': '',
            'confidence': 0,
            'error': str(e),
            'message': 'Error processing PAN verification'
        }), 400

@app.route("/panResizeMAR", methods=["POST", "GET"])
def panresizeMAR():
    try:
        if request.files and 'file' in request.files:   
            if request.files['file'].filename != "":
                file_bytes = request.files['file'].read()
                height = int(request.form.get('height', 0))
                width = int(request.form.get('width', 0))
                result_bytes = panResize.resize_pan_mar(file_bytes, height, width)
                if result_bytes:
                    return send_file(BytesIO(result_bytes), mimetype='image/jpeg', as_attachment=True, download_name='resized.jpeg')
                else:
                    return "Inappropriate size", 400
    except Exception as e:
        print(f"Error in PAN resize MAR: {e}")
        return f"Error: {str(e)}", 500

@app.route("/panResizeHard", methods=["POST", "GET"])
def panresizehard():
    try:
        if request.files and 'file' in request.files:   
            if request.files['file'].filename != "":
                file_bytes = request.files['file'].read()
                height = int(request.form.get('height', 0))
                width = int(request.form.get('width', 0))
                result_bytes = panResize.resize_pan_hard(file_bytes, height=height, width=width)
                if result_bytes:
                    return send_file(BytesIO(result_bytes), mimetype='image/jpeg', as_attachment=True, download_name='resized.jpeg')
                else:
                    return "Inappropriate size", 400
    except Exception as e:
        print(f"Error in PAN resize hard: {e}")
        return f"Error: {str(e)}", 500

@app.route("/aadharResizeHard", methods=["POST", "GET"])
def aadhar_resize_hard():
    try:
        if request.files and 'file' in request.files:   
            if request.files['file'].filename != "":
                file_bytes = request.files['file'].read()
                height = int(request.form.get('height', 0))
                width = int(request.form.get('width', 0))
                result_bytes = aadharResize.resize_aadhar_hard(file_bytes, height=height, width=width)
                if result_bytes:
                    return send_file(BytesIO(result_bytes), mimetype='image/jpeg', as_attachment=True, download_name='resized.jpeg')
                else:
                    return "Inappropriate size", 400
    except Exception as e:
        print(f"Error in Aadhar resize hard: {e}")
        return f"Error: {str(e)}", 500

@app.route("/aadharResizeMAR", methods=["POST", "GET"])
def aadhar_resize_mar():
    try:
        if request.files and 'file' in request.files:   
            if request.files['file'].filename != "":
                file_bytes = request.files['file'].read()
                height = int(request.form.get('height', 0))
                width = int(request.form.get('width', 0))
                result_bytes = aadharResize.resize_aadhar_mar(file_bytes, height=height, width=width)
                if result_bytes:
                    return send_file(BytesIO(result_bytes), mimetype='image/jpeg', as_attachment=True, download_name='resized.jpeg')
                else:
                    return "Inappropriate size", 400
    except Exception as e:
        print(f"Error in Aadhar resize MAR: {e}")
        return f"Error: {str(e)}", 500

@app.route("/reduceSize", methods=["POST", "GET"])
def reduce():
    try:
        if request.files and 'file' in request.files:   
            if request.files['file'].filename != "":
                file_bytes = request.files['file'].read()
                result_bytes = reduceSize.reduce_storage(file_bytes)
                if result_bytes:
                    return send_file(BytesIO(result_bytes), mimetype='image/jpeg', as_attachment=True, download_name='reduced.jpeg')
                else:
                    return "Error reducing size", 500
    except Exception as e:
        print(f"Error in reduce size: {e}")
        return f"Error: {str(e)}", 500

# General image resize endpoints (for any image)
@app.route("/resizeMAR", methods=["POST", "GET"])
def resize_mar():
    """General image resize maintaining aspect ratio"""
    try:
        if request.files and 'file' in request.files:   
            if request.files['file'].filename != "":
                file_bytes = request.files['file'].read()
                height = int(request.form.get('height', 0))
                width = int(request.form.get('width', 0))
                
                # Use Pillow to resize
                from PIL import Image
                img = Image.open(BytesIO(file_bytes))
                
                # Calculate height maintaining aspect ratio
                aspect_ratio = img.height / img.width
                new_height = int(width * aspect_ratio)
                
                resized = img.resize((width, new_height), Image.Resampling.LANCZOS)
                
                output = BytesIO()
                resized.save(output, format='JPEG', quality=95)
                result_bytes = output.getvalue()
                
                return send_file(BytesIO(result_bytes), mimetype='image/jpeg', as_attachment=True, download_name='resized.jpeg')
    except Exception as e:
        print(f"Error in general resize MAR: {e}")
        return f"Error: {str(e)}", 500

@app.route("/resizeHard", methods=["POST", "GET"])
def resize_hard():
    """General image hard resize to exact dimensions"""
    try:
        if request.files and 'file' in request.files:   
            if request.files['file'].filename != "":
                file_bytes = request.files['file'].read()
                height = int(request.form.get('height', 0))
                width = int(request.form.get('width', 0))
                
                # Use Pillow to resize
                from PIL import Image
                img = Image.open(BytesIO(file_bytes))
                
                resized = img.resize((width, height), Image.Resampling.LANCZOS)
                
                output = BytesIO()
                resized.save(output, format='JPEG', quality=95)
                result_bytes = output.getvalue()
                
                return send_file(BytesIO(result_bytes), mimetype='image/jpeg', as_attachment=True, download_name='resized.jpeg')
    except Exception as e:
        print(f"Error in general resize hard: {e}")
        return f"Error: {str(e)}", 500

# Health check endpoint for Vercel
@app.route("/health")
def health():
    return {"status": "healthy"}, 200

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
