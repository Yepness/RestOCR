# Text Extraction API with Tesseract

## Description
This API provides a service to extract text from images using the Tesseract OCR (Optical Character Recognition) library. Users can send an image and choose between two extraction types: 'data' to receive results as a list of text based on the specified confidence level, or 'string' to get the extracted text directly as a single string.

## Usage
### Method
- POST

### URL
- https://localhost:5000/rest_tessdata

### Request Parameters

| Parameter | Type    | Description                                                                                   |
|-----------|---------|-----------------------------------------------------------------------------------------------|
| image     | File    | Image containing the text to be extracted.                                                   |
| type      | String  | Desired extraction type. Can be 'data' or 'string'.                                           |
| conf      | Integer | (Required if type=data) Confidence level in percentage for text extraction. Ranges from 0 to 100. |

### Responses

| Status Code | Description                   | Response Body                                      |
|-------------|-------------------------------|---------------------------------------------------|
| 200         | Success                       | List of strings (if type=data) or text (if type=string) |
| 400         | Invalid Request               | Error message describing the issue encountered.   |
| 500         | Internal Server Error         | Detailed error message.                           |

## Text Extraction Request with Specific Confidence (type=data)

**POST** /rest_tessdata  
Content-Type: multipart/form-data  

```plaintext
image: [image file]
type: data
conf: 70
```

Response (200 OK):
```json
[
    "Extracted text 1",
    "Extracted text 2",
    ...
]
```

## General Text Extraction Request (type=string)

**POST** /rest_tessdata  
Content-Type: multipart/form-data  

```plaintext
image: [image file]
type: string
```

Response (200 OK):
```json
"Extracted text"
```

## Notes

Ensure that all required parameters are provided correctly.

The confidence level (`conf`) measures how reliable the text extraction is. Higher values result in stricter filtering for reliable text, while lower values may include more text but could introduce potential errors.
