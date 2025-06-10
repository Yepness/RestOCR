
# Text Extraction API with Tesseract and PaddleOCR

## Description

This API provides a comprehensive service to extract text from images using both Tesseract OCR and PaddleOCR libraries. Users can send an image and choose between two extraction types: 'data' to receive results as a list of text based on the specified confidence level, or 'string' to get the extracted text directly as a single formatted string. The API returns results from both OCR engines for comparison and better accuracy.

## Features

* **Dual OCR Engine Support** : Combines Tesseract and PaddleOCR for enhanced text extraction
* **Flexible Output Formats** : Choose between structured data or formatted strings
* **Confidence-based Filtering** : Filter Tesseract results by confidence level
* **Intelligent Text Formatting** : PaddleOCR results are formatted with proper line breaks based on text positioning
* **Portuguese Language Support** : Optimized for Portuguese text recognition

## Usage

### Method

* POST

### URL

* `http://localhost:5000/v1/RestOCR`

### Request Parameters

| Parameter | Type    | Description                                                                                                 |
| --------- | ------- | ----------------------------------------------------------------------------------------------------------- |
| image     | File    | Image containing the text to be extracted.                                                                  |
| type      | String  | Desired extraction type. Can be 'data' or 'string'.                                                         |
| conf      | Integer | (Required if type=data) Confidence level in percentage for Tesseract text extraction. Ranges from 0 to 100. |

### Responses

| Status Code | Description           | Response Body                                   |
| ----------- | --------------------- | ----------------------------------------------- |
| 200         | Success               | JSON object with results from both OCR engines  |
| 400         | Invalid Request       | Error message describing the issue encountered. |
| 500         | Internal Server Error | Detailed error message.                         |

## API Examples

### Text Extraction Request with Specific Confidence (type=data)

**POST** `/v1/RestOCR`

Content-Type: multipart/form-data

```plaintext
image: [image file]
type: data
conf: 70
```

Response (200 OK):

```json
{
    "tesseract": [
        "Extracted text 1",
        "Extracted text 2",
        "Extracted text 3"
    ],
    "paddle": [
        "Text from PaddleOCR 1",
        "Text from PaddleOCR 2",
        "Text from PaddleOCR 3"
    ]
}
```

### General Text Extraction Request (type=string)

**POST** `/v1/RestOCR`

Content-Type: multipart/form-data

```plaintext
image: [image file]
type: string
```

Response (200 OK):

```json
{
    "tesseract": "Complete extracted text from Tesseract\nwith line breaks preserved",
    "paddle": "Complete extracted text from PaddleOCR\nwith intelligent formatting\nand proper line breaks"
}
```

## OCR Engine Comparison

### Tesseract OCR

* **Strengths** : Mature, widely-used, good for standard documents
* **Configuration** : Uses PSM 6 (uniform block of text) with Portuguese language support
* **Confidence Filtering** : Results can be filtered by confidence level (0-100%)

### PaddleOCR

* **Strengths** : Modern deep learning approach, better for complex layouts and varied fonts
* **Smart Formatting** : Automatically formats text with proper line breaks based on text positioning
* **Built-in Quality** : Uses internal confidence scoring, no manual threshold needed

## Error Handling

The API includes comprehensive error handling for:

* Missing required parameters
* Invalid file uploads
* Processing errors from either OCR engine
* Temporary file management

## Notes

* **Performance** : PaddleOCR is initialized once at startup for better performance on subsequent requests
* **Temporary Files** : Uploaded images are automatically cleaned up after processing
* **Confidence Level** : The `conf` parameter only affects Tesseract results. PaddleOCR uses its own internal confidence scoring
* **Language Support** : Both engines are configured for Portuguese text recognition
* **GPU Acceleration** : The API will use GPU acceleration if available, otherwise falls back to CPU processing

## Installation Requirements

```bash
pip install flask flask-cors opencv-python pandas pytesseract paddleocr
```

## Running the API

```bash
python app.py
```

The API will be available at `http://localhost:5000` with debug mode enabled.
