# API for Document Resizing, Validation and Verification

**Project Year:** 2021 (2020_CSE_15)

A Flask-based web application for verifying and resizing Indian government documents (Aadhar Card, PAN Card) using OCR technology and image processing.

## ⚠️ Important Note on Validation

This project uses **algorithmic validation** and **OCR-based verification**:
- **Format validation** - Checks number structure
- **Checksum validation** - Verhoeff algorithm for Aadhar
- **Document authenticity** - Keyword detection via OCR
- **Structure validation** - Per government specifications

**NOT implemented:** Direct web scraping of UIDAI/NSDL websites (requires CAPTCHA solving, authentication, and violates ToS)

## 🎯 Features

### Aadhar Card Verification
- **OCR-based text extraction** using Google Cloud Vision API
- **Document authenticity verification** - Checks for official keywords (GOVERNMENT OF INDIA, आधार, UIDAI)
- **Number validation** using Verhoeff algorithm (official UIDAI checksum)
- **Format validation** - 12 digits starting with 2-9
- **Confidence scoring** based on keyword matches and text quality
- **Image resizing** with aspect ratio maintenance or hard resize options

### PAN Card Verification
- **OCR-based text extraction** using Google Cloud Vision API
- **Document authenticity verification** - Checks for official keywords (INCOME TAX DEPARTMENT, PAN)
- **Structure validation** - AAAAA9999A format per Income Tax specifications
- **Holder type detection** - Identifies Individual, Company, HUF, etc.
- **4th character validation** - Ensures valid entity type (P, C, H, F, A, T, B, L, J, G)
- **Confidence scoring** based on keyword matches and text quality
- **Image resizing** with aspect ratio maintenance or hard resize options

### General Image Processing
- **Resize any image** to custom dimensions
- **Maintain aspect ratio** or hard resize to exact dimensions
- **File size reduction** with quality optimization
- **Supports** JPG, PNG, JPEG formats (max 16MB)

## 🛠️ Technology Stack

- **Backend**: Flask 3.0.0
- **OCR**: Google Cloud Vision API 3.5.0
- **Image Processing**: Pillow 10.1.0
- **Server**: Gunicorn 21.2.0
- **Additional**: Requests, BeautifulSoup4

## 📋 Prerequisites

1. **Python 3.11+**
2. **Google Cloud Account** with Vision API enabled
3. **Service Account JSON credentials** from Google Cloud

## 🚀 Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/kishorep26/API-Document-Resize.git
cd API-Document-Resize
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Set Up Google Cloud Vision API

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable **Cloud Vision API**
4. Create a **Service Account**:
   - Go to IAM & Admin → Service Accounts
   - Click "Create Service Account"
   - Grant "Cloud Vision AI Service Agent" role
5. Create and download **JSON key**:
   - Click on service account
   - Go to "Keys" tab
   - Add Key → Create new key → JSON
   - Save the downloaded file

### 4. Configure Credentials

**For Local Development:**
```bash
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/credentials.json"
```

**For Vercel Deployment:**
- Add environment variable in Vercel dashboard
- Name: `GOOGLE_APPLICATION_CREDENTIALS`
- Value: Paste entire JSON file content

### 5. Run the Application

**Local Development:**
```bash
python app.py
```
Visit: `http://localhost:5000`

**Production (Vercel):**
```bash
vercel deploy
```

## 📡 API Endpoints

### Pages
- `GET /` - Home page
- `GET /aadhar` - Aadhar verification page
- `GET /pan` - PAN verification page
- `GET /resize` - General image resize page

### Verification APIs
- `POST /aadharVerification` - Verify Aadhar card (image or number)
- `POST /panVerification` - Verify PAN card (image or number)

### Resize APIs (Document-specific)
- `POST /aadharResizeMAR` - Resize Aadhar maintaining aspect ratio
- `POST /aadharResizeHard` - Hard resize Aadhar to exact dimensions
- `POST /panResizeMAR` - Resize PAN maintaining aspect ratio
- `POST /panResizeHard` - Hard resize PAN to exact dimensions

### Resize APIs (General)
- `POST /resizeMAR` - Resize any image maintaining aspect ratio
- `POST /resizeHard` - Hard resize any image to exact dimensions
- `POST /reduceSize` - Reduce file size with quality optimization

## 📝 API Response Format

### Verification Response
```json
{
  "valid": true,
  "number": "2345 6789 1234",
  "confidence": 85,
  "message": "Aadhar card verified successfully",
  "holder_type": "Individual"
}
```

### Fields
- `valid` (boolean) - Whether document/number is valid
- `number` (string) - Extracted or formatted number
- `confidence` (integer) - Confidence score 0-100
- `message` (string) - Human-readable result message
- `holder_type` (string) - PAN holder type (PAN only)

## 🔍 How Verification Works

### Aadhar Card Validation
1. **OCR Extraction** - Extracts all text from image using Google Cloud Vision
2. **Keyword Detection** - Checks for official Aadhar keywords (min 2 required):
   - "GOVERNMENT OF INDIA"
   - "आधार" (Aadhaar in Hindi)
   - "UNIQUE IDENTIFICATION"
   - "UIDAI"
3. **Number Extraction** - Finds 12-digit number matching pattern
4. **Verhoeff Validation** - Validates checksum using official UIDAI algorithm
5. **Confidence Calculation** - Scores based on keywords found and text quality

### PAN Card Validation
1. **OCR Extraction** - Extracts all text from image using Google Cloud Vision
2. **Keyword Detection** - Checks for official PAN keywords (min 2 required):
   - "INCOME TAX DEPARTMENT"
   - "GOVT OF INDIA"
   - "PERMANENT ACCOUNT NUMBER"
3. **Number Extraction** - Finds 10-character code matching AAAAA9999A pattern
4. **Structure Validation** - Validates per Income Tax Department specifications:
   - First 5 characters: Letters
   - 4th character: Valid entity type (P/C/H/F/A/T/B/L/J/G)
   - Next 4 characters: Digits
   - Last character: Letter
5. **Holder Type Detection** - Identifies entity type from 4th character
6. **Confidence Calculation** - Scores based on keywords found and text quality

## 🎨 User Interface

- **Modern gradient design** with color-coded pages
- **Tabbed interface** for Verify and Resize functions
- **Drag & drop file upload**
- **Real-time image preview**
- **Confidence score visualization** with progress bars
- **Color-coded results** (Green=Success, Red=Error, Blue=Info)
- **Responsive design** for mobile and desktop

## 🧪 Testing

### Without Google Cloud (Number Validation Only)
```
Aadhar: 234567891234 ✓
PAN: ABCDE1234F ✓
```

### With Google Cloud (Full Features)
1. Upload Aadhar/PAN card image
2. OCR extracts text and number
3. Validates document authenticity
4. Returns confidence score
5. Allows image resizing

## 📦 Deployment

### Vercel (Recommended)
1. Push code to GitHub
2. Import repository in Vercel
3. Add `GOOGLE_APPLICATION_CREDENTIALS` environment variable
4. Deploy automatically

### Other Platforms
- Ensure Python 3.11+ runtime
- Set `GOOGLE_APPLICATION_CREDENTIALS` environment variable
- Install dependencies from `requirements.txt`
- Run with Gunicorn: `gunicorn app:app`

## 🔒 Security & Privacy

- Images processed in memory only (not stored)
- No database or persistent storage
- Credentials via environment variables only
- HTTPS recommended for production
- No external API calls except Google Cloud Vision

## ⚠️ Important Notes

### Validation Limitations
- **UIDAI/Income Tax APIs** are not publicly available
- This project uses:
  - Official algorithms (Verhoeff for Aadhar)
  - Government-specified formats
  - Keyword-based authenticity checks
- For production use, official API access is recommended

### Google Cloud Vision API
- **Free tier**: 1,000 requests/month
- **Paid tier**: $1.50 per 1,000 requests
- Required for OCR functionality
- See `GOOGLE_CLOUD_SETUP.md` for detailed setup

## 📚 Project Structure

```
.
├── app.py                      # Main Flask application
├── requirements.txt            # Python dependencies
├── runtime.txt                 # Python version for deployment
├── vercel.json                # Vercel configuration
├── BackEnd/
│   ├── aadharVerification.py  # Aadhar validation logic
│   ├── panVerification.py     # PAN validation logic
│   ├── aadharResize.py        # Aadhar image resizing
│   ├── panResize.py           # PAN image resizing
│   └── reduceSize.py          # File size reduction
└── Frontend/
    ├── Templates/
    │   ├── index.html         # Home page
    │   ├── aadhar.html        # Aadhar verification page
    │   ├── pan.html           # PAN verification page
    │   └── resize.html        # General resize page
    └── static/
        ├── css/
        ├── js/
        └── images/
```

## 🤝 Contributing

This is an educational project demonstrating:
- OCR integration
- Document validation algorithms
- Image processing
- Modern web UI design
- Flask API development

## 📄 License

Educational project - 2020_CSE_15

## 🔗 Links

- **Repository**: https://github.com/kishorep26/API-Document-Resize
- **Google Cloud Console**: https://console.cloud.google.com/
- **Vercel**: https://vercel.com/

---

**Keywords**: Web API, Resize, OCR, Validation, Verification, Aadhaar, PAN, Document Processing, Flask, Google Cloud Vision
