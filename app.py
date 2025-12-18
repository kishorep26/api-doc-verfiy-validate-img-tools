import re
import sys
import os

# Add BackEnd directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'BackEnd'))

from flask import Flask, render_template, Response, request, send_file
from werkzeug.utils import secure_filename
import cv2
import numpy

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

@app.route("/aadharVerification", methods=['POST', 'GET'])
def aadhar():
    try:
        if request.files and 'file' in request.files:   
            if request.files['file'].filename != "":
                file = request.files['file'].read()
                npimg = numpy.frombuffer(file, numpy.uint8)
                img = cv2.imdecode(npimg, cv2.IMREAD_COLOR)
                a, num = aadharVerification.aadhar_auth_img(img)
                if a:
                    return Response(str({'number': str(num), 'valid': True}), status=200, mimetype='application/json')
                else:
                    return Response(str({'number': '', 'valid': False}), status=200, mimetype='application/json')
        else:
            number = request.form.get("number", "")
            a, num = aadharVerification.aadhar_auth_number(number)
            if a:
                return Response(str({'number': str(num), 'valid': True}), status=200, mimetype='application/json')
            else:
                return Response(str({'number': '', 'valid': False}), status=200, mimetype='application/json')
    except Exception as e:
        print(f"Error in aadhar verification: {e}")
        return Response(str({'number': '', 'valid': False, 'error': str(e)}), status=403, mimetype='application/json')

@app.route("/panVerification", methods=['POST', 'GET'])
def pan():
    try:
        if request.files and 'file' in request.files:   
            if request.files['file'].filename != "":
                file = request.files['file'].read()
                npimg = numpy.frombuffer(file, numpy.uint8)
                img = cv2.imdecode(npimg, cv2.IMREAD_COLOR)
                a, num = panVerification.pan_auth_img(img)
                if a:
                    return Response(str({'number': str(num), 'valid': True}), status=200, mimetype='application/json')
                else:
                    return Response(str({'number': '', 'valid': False}), status=200, mimetype='application/json')
        else:
            number = request.form.get("number", "")
            a, num = panVerification.pan_auth_number(number)
            if a:
                return Response(str({'number': str(num), 'valid': True}), status=200, mimetype='application/json')
            else:
                return Response(str({'number': '', 'valid': False}), status=200, mimetype='application/json')
    except Exception as e:
        print(f"Error in PAN verification: {e}")
        return Response(str({'number': '', 'isvalid': False, 'error': str(e)}), status=400, mimetype='application/json')

@app.route("/panResizeMAR", methods=["POST", "GET"])
def panresizeMAR():
    try:
        if request.files and 'file' in request.files:   
            if request.files['file'].filename != "":
                file = request.files['file'].read()
                npimg = numpy.frombuffer(file, numpy.uint8)
                img = cv2.imdecode(npimg, cv2.IMREAD_COLOR)
                height = int(request.form.get('height', 0))
                width = int(request.form.get('width', 0))
                a = panResize.resize_pan_mar(img, height, width)
                if a[0]:
                    output_path = "/tmp/resized.jpeg"
                    cv2.imwrite(output_path, a[1])
                    return send_file(output_path, mimetype='image/jpeg') 
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
                file = request.files['file'].read()
                npimg = numpy.frombuffer(file, numpy.uint8)
                img = cv2.imdecode(npimg, cv2.IMREAD_COLOR)
                height = int(request.form.get('height', 0))
                width = int(request.form.get('width', 0))
                a = panResize.resize_pan_hard(img, height=height, width=width)
                if a[0]:
                    output_path = "/tmp/resized.jpeg"
                    cv2.imwrite(output_path, a[1])
                    return send_file(output_path, mimetype='image/jpeg') 
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
                file = request.files['file'].read()
                npimg = numpy.frombuffer(file, numpy.uint8)
                img = cv2.imdecode(npimg, cv2.IMREAD_COLOR)
                height = int(request.form.get('height', 0))
                width = int(request.form.get('width', 0))
                a = aadharResize.resize_aadhar_hard(img, height=height, width=width)
                if a[0]:
                    output_path = "/tmp/resized.jpeg"
                    cv2.imwrite(output_path, a[1])
                    return send_file(output_path, mimetype='image/jpeg') 
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
                file = request.files['file'].read()
                npimg = numpy.frombuffer(file, numpy.uint8)
                img = cv2.imdecode(npimg, cv2.IMREAD_COLOR)
                height = int(request.form.get('height', 0))
                width = int(request.form.get('width', 0))
                a = aadharResize.resize_aadhar_mar(img, height=height, width=width)
                if a[0]:
                    output_path = "/tmp/resized.jpeg"
                    cv2.imwrite(output_path, a[1])
                    return send_file(output_path, mimetype='image/jpeg') 
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
                file = request.files['file'].read()
                npimg = numpy.frombuffer(file, numpy.uint8)
                img = cv2.imdecode(npimg, cv2.IMREAD_COLOR)
                a = reduceSize.reduce_storeage(img)
                if a:
                    return send_file("/tmp/reduced.jpeg", mimetype='image/jpeg') 
                else:
                    return "Error reducing size", 500
    except Exception as e:
        print(f"Error in reduce size: {e}")
        return f"Error: {str(e)}", 500

# Health check endpoint for Vercel
@app.route("/health")
def health():
    return {"status": "healthy"}, 200

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
