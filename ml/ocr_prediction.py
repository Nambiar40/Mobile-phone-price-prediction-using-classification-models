import pytesseract
from PIL import Image
import cv2
import sys
import os

# Set Tesseract path (Windows typically installs it here)
tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
if os.path.exists(tesseract_cmd):
    pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
else:
    tesseract_cmd = r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe'
    if os.path.exists(tesseract_cmd):
        pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
    else:
        print("Tesseract executable not found. Please verify the installation path.")
        sys.exit(1)

def extract_text(image_path):
    print(f"Reading image: {image_path}")
    
    # Check if image exists
    if not os.path.exists(image_path):
        print(f"Error: File not found -> {image_path}")
        return

    # Load image using OpenCV for preprocessing (optional, helps with OCR accuracy)
    img = cv2.imread(image_path)
    
    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Use thresholding to make text clearer (optional)
    # _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)

    # Perform OCR
    print("Performing OCR extraction...")
    text = pytesseract.image_to_string(gray)
    
    print("\n" + "="*50)
    print("Extracted Text:")
    print("="*50)
    print(text.strip())
    print("="*50)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        extract_text(sys.argv[1])
    else:
        print("Usage: python ocr_prediction.py <path_to_image>")
