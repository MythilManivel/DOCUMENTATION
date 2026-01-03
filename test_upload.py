#!/usr/bin/env python
"""Test script to verify the upload endpoint works."""

import requests
import os

# Create a test PDF file if it doesn't exist
test_pdf = "test.pdf"
if not os.path.exists(test_pdf):
    # Create a minimal PDF
    with open(test_pdf, 'wb') as f:
        f.write(b'%PDF-1.4\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n3 0 obj\n<< /Type /Page /Parent 2 0 R /Resources << /Font << /F1 << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> >> >> /MediaBox [0 0 612 792] /Contents 4 0 R >>\nendobj\n4 0 obj\n<< >>\nstream\nBT\n/F1 12 Tf\n100 700 Td\n(Hello World) Tj\nET\nendstream\nendobj\nxref\n0 5\n0000000000 65535 f\n0000000009 00000 n\n0000000058 00000 n\n0000000115 00000 n\n0000000259 00000 n\ntrailer\n<< /Size 5 /Root 1 0 R >>\nstartxref\n318\n%%EOF\n')

print("Testing upload endpoint...")
try:
    with open(test_pdf, 'rb') as f:
        files = {'file': f}
        response = requests.post('http://127.0.0.1:5000/upload', files=files)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
except Exception as e:
    print(f"Error: {e}")

os.remove(test_pdf) if os.path.exists(test_pdf) else None
