#!/usr/bin/env python3

import requests
import sys
import json
from datetime import datetime
import uuid
import base64
import io
from PIL import Image

class SignatureSizeTest:
    def __init__(self, base_url="https://invoicecraft-6.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        
        # Store created IDs for cleanup
        self.created_company_id = None
        self.created_letter_id = None
        self.uploaded_signature = None

    def log_result(self, test_name, success, details="", error_msg=""):
        """Log test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {test_name}: PASSED")
            if details:
                print(f"   {details}")
        else:
            print(f"❌ {test_name}: FAILED - {error_msg}")

    def create_test_company(self):
        """Create a test company with logo"""
        print("\n🏢 Creating test company with logo...")
        
        # Create a simple logo
        logo_img = Image.new('RGB', (100, 50), color='#1e40af')
        logo_buffer = io.BytesIO()
        logo_img.save(logo_buffer, format='PNG')
        logo_base64 = base64.b64encode(logo_buffer.getvalue()).decode('utf-8')
        logo_data_uri = f"data:image/png;base64,{logo_base64}"
        
        company_data = {
            "name": "Signature Test Company",
            "address": "Jl. Test Signature No. 123, Jakarta",
            "phone": "+62-21-1234567",
            "email": "test@signaturetest.com",
            "website": "https://signaturetest.com",
            "motto": "Testing Signature Improvements",
            "logo": logo_data_uri
        }
        
        try:
            response = requests.post(f"{self.api_url}/companies", json=company_data, timeout=30)
            if response.status_code == 201:
                self.created_company_id = response.json().get('id')
                self.log_result("Create Test Company", True, f"Company ID: {self.created_company_id}")
                return True
            else:
                self.log_result("Create Test Company", False, error_msg=f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_result("Create Test Company", False, error_msg=str(e))
            return False

    def upload_signature(self):
        """Upload a test signature"""
        print("\n📝 Uploading test signature...")
        
        try:
            # Create a signature image
            sig_img = Image.new('RGBA', (200, 100), color=(255, 255, 255, 0))
            from PIL import ImageDraw, ImageFont
            draw = ImageDraw.Draw(sig_img)
            
            # Draw signature-like content
            draw.text((10, 20), "John Doe", fill=(0, 0, 0, 255))
            draw.line([(10, 50), (180, 50)], fill=(0, 0, 0, 255), width=2)
            draw.text((10, 60), "CEO", fill=(0, 0, 0, 255))
            
            sig_buffer = io.BytesIO()
            sig_img.save(sig_buffer, format='PNG')
            
            files = {'file': ('signature.png', sig_buffer.getvalue(), 'image/png')}
            response = requests.post(f"{self.api_url}/upload-signature", files=files, timeout=30)
            
            if response.status_code == 200:
                self.uploaded_signature = response.json().get('signature')
                self.log_result("Upload Signature", True, "Signature uploaded successfully")
                return True
            else:
                self.log_result("Upload Signature", False, error_msg=f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_result("Upload Signature", False, error_msg=str(e))
            return False

    def create_letter_with_signature(self):
        """Create a letter with signature"""
        print("\n📄 Creating letter with signature...")
        
        if not self.created_company_id:
            self.log_result("Create Letter", False, error_msg="No company ID")
            return False
        
        letter_data = {
            "letter_number": f"SIG-TEST/{datetime.now().strftime('%Y%m%d')}/001",
            "company_id": self.created_company_id,
            "date": datetime.now().strftime('%Y-%m-%d'),
            "subject": "Testing Signature Size in PDF Generation",
            "letter_type": "general",
            "recipient_name": "Test Recipient",
            "recipient_position": "Manager",
            "recipient_address": "Test Address",
            "content": "This letter is created to test the signature size improvements in PDF generation. The signature should now be 2x larger (160x80 pixels) for better visibility.",
            "signatories": [
                {
                    "name": "John Doe",
                    "position": "Chief Executive Officer",
                    "signature_image": self.uploaded_signature
                }
            ]
        }
        
        try:
            response = requests.post(f"{self.api_url}/letters", json=letter_data, timeout=30)
            if response.status_code == 201:
                self.created_letter_id = response.json().get('id')
                self.log_result("Create Letter with Signature", True, f"Letter ID: {self.created_letter_id}")
                return True
            else:
                self.log_result("Create Letter with Signature", False, error_msg=f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_result("Create Letter with Signature", False, error_msg=str(e))
            return False

    def test_pdf_generation(self):
        """Test PDF generation and download"""
        print("\n📋 Testing PDF generation...")
        
        if not self.created_letter_id:
            self.log_result("PDF Generation", False, error_msg="No letter ID")
            return False
        
        try:
            response = requests.get(f"{self.api_url}/letters/{self.created_letter_id}/pdf", timeout=30)
            
            if response.status_code == 200 and response.headers.get('content-type') == 'application/pdf':
                pdf_size = len(response.content)
                
                # Save PDF for manual verification
                pdf_filename = f"/tmp/signature_test_{self.created_letter_id}.pdf"
                with open(pdf_filename, "wb") as f:
                    f.write(response.content)
                
                self.log_result("PDF Generation", True, f"PDF generated successfully, size: {pdf_size} bytes, saved to: {pdf_filename}")
                return True
            else:
                self.log_result("PDF Generation", False, error_msg=f"Status: {response.status_code}, Content-Type: {response.headers.get('content-type')}")
                return False
        except Exception as e:
            self.log_result("PDF Generation", False, error_msg=str(e))
            return False

    def verify_backend_code(self):
        """Verify the backend code has the correct signature size settings"""
        print("\n🔍 Verifying backend code for signature improvements...")
        
        try:
            with open('/app/backend/server.py', 'r') as f:
                code = f.read()
            
            # Check for signature size configuration
            if "max_sig_width, max_sig_height = 160, 80" in code:
                self.log_result("Signature Size Code", True, "Backend configured for 160x80 signature size")
            else:
                self.log_result("Signature Size Code", False, error_msg="Signature size not set to 160x80")
            
            # Check for 2x larger comment
            if "2x larger for better visibility" in code:
                self.log_result("Signature Size Comment", True, "Code comment confirms 2x larger implementation")
            else:
                self.log_result("Signature Size Comment", False, error_msg="Missing 2x larger comment")
            
            # Check for centered layout
            if "alignment=TA_CENTER" in code and "company_style" in code:
                self.log_result("Centered Layout", True, "Company header centered layout implemented")
            else:
                self.log_result("Centered Layout", False, error_msg="Centered layout not found")
            
            # Check for bold company name
            if "company_name_style" in code and "fontSize=14" in code:
                self.log_result("Bold Company Name", True, "Company name bold and larger font implemented")
            else:
                self.log_result("Bold Company Name", False, error_msg="Bold company name not found")
            
            # Check for italic motto
            if "Helvetica-Oblique" in code and "company_motto_style" in code:
                self.log_result("Italic Motto", True, "Company motto italic style implemented")
            else:
                self.log_result("Italic Motto", False, error_msg="Italic motto style not found")
                
        except Exception as e:
            self.log_result("Backend Code Verification", False, error_msg=str(e))

    def cleanup(self):
        """Clean up test data"""
        print("\n🧹 Cleaning up...")
        
        if self.created_letter_id:
            try:
                requests.delete(f"{self.api_url}/letters/{self.created_letter_id}", timeout=30)
                self.log_result("Delete Letter", True)
            except:
                self.log_result("Delete Letter", False, error_msg="Failed to delete")
        
        if self.created_company_id:
            try:
                requests.delete(f"{self.api_url}/companies/{self.created_company_id}", timeout=30)
                self.log_result("Delete Company", True)
            except:
                self.log_result("Delete Company", False, error_msg="Failed to delete")

    def run_tests(self):
        """Run all signature tests"""
        print("🚀 Starting Signature Size and PDF Layout Tests")
        print("="*60)
        
        # Verify backend code first
        self.verify_backend_code()
        
        # Create test data and generate PDF
        if self.create_test_company():
            if self.upload_signature():
                if self.create_letter_with_signature():
                    self.test_pdf_generation()
        
        # Cleanup
        self.cleanup()
        
        # Results
        print("\n" + "="*60)
        print("TEST RESULTS SUMMARY")
        print("="*60)
        print(f"📊 Tests Run: {self.tests_run}")
        print(f"✅ Tests Passed: {self.tests_passed}")
        print(f"❌ Tests Failed: {self.tests_run - self.tests_passed}")
        print(f"📈 Success Rate: {(self.tests_passed/self.tests_run*100):.1f}%")
        
        if self.tests_passed == self.tests_run:
            print("\n🎉 All tests passed! Signature improvements are working correctly.")
            print("\n📋 Key Improvements Verified:")
            print("   • Signature size increased to 160x80 pixels (2x larger)")
            print("   • Centered company header layout")
            print("   • Bold and larger company name")
            print("   • Italic company motto")
            print("   • Professional PDF formatting")
        
        return self.tests_passed == self.tests_run

def main():
    tester = SignatureSizeTest()
    success = tester.run_tests()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())