# API for Document Resizing, Validation and Verification

## Overview
A powerful web application for document processing that combines automated resizing, validation, and verification capabilities using advanced image analysis. Built with Flask and Google Cloud Vision API, this tool provides comprehensive document management features including intelligent image manipulation, format validation, and authenticity verification for various document types.

## Key Features
- Automated document resizing with aspect ratio preservation
- Google Cloud Vision API integration for intelligent image analysis
- Document validation and authenticity verification
- Multi-format support (PDF, JPG, PNG, etc.)
- Batch processing capabilities for multiple documents
- RESTful API endpoints for integration
- Web-based frontend interface for easy access
- Detailed verification reports and analytics
- Secure document handling and storage
- Real-time processing status updates

## Technology Stack
- Backend: Python, Flask
- Frontend: HTML, CSS, JavaScript
- Image Processing: PIL/Pillow, OpenCV
- AI/ML: Google Cloud Vision API
- API: RESTful architecture
- Deployment: Vercel-compatible
- Shell Scripts: Automation utilities

## Getting Started
1. Install dependencies: pip install -r requirements.txt
2. Set up Google Cloud Vision API credentials
3. Configure environment variables for API keys
4. Run the Flask application: python app.py or bash run.sh
5. Access the web interface at http://localhost:5000
6. Upload documents for processing via API or web interface
7. View verification reports in the Reports section

## Deployment
Configured for deployment on Vercel or any Python hosting platform. Compatible with cloud services like AWS, Google Cloud Platform, or Azure.
