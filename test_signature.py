#!/usr/bin/env python3

import requests
import base64
import io
from PIL import Image

def test_signature_upload():
    # Create a proper test image
    img = Image.new('RGB', (100, 50), color='white')
    
    # Save to bytes
    img_buffer = io.BytesIO()
    img.save(img_buffer, format='PNG')
    img_bytes = img_buffer.getvalue()
    
    print(f"Created image with {len(img_bytes)} bytes")
    
    # Test the upload
    url = "https://invoicecraft-6.preview.emergentagent.com/api/upload-signature"
    files = {'file': ('signature.png', img_bytes, 'image/png')}
    
    try:
        response = requests.post(url, files=files, timeout=30)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Success! Signature length: {len(data.get('signature', ''))}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_signature_upload()