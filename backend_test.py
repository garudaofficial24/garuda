#!/usr/bin/env python3

import requests
import sys
import json
from datetime import datetime, timedelta
import uuid

class InvoiceQuotationAPITester:
    def __init__(self, base_url="https://invoicecraft-6.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []
        
        # Store created IDs for cleanup and testing
        self.created_company_id = None
        self.created_item_id = None
        self.created_invoice_id = None
        self.created_quotation_id = None
        self.created_letter_id = None
        self.uploaded_signature = None

    def log_result(self, test_name, success, details="", error_msg=""):
        """Log test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {test_name}: PASSED")
        else:
            print(f"❌ {test_name}: FAILED - {error_msg}")
        
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details,
            "error": error_msg
        })

    def run_test(self, name, method, endpoint, expected_status, data=None, return_response=False):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}

        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=30)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=30)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers, timeout=30)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=30)

            success = response.status_code == expected_status
            
            if success:
                self.log_result(name, True, f"Status: {response.status_code}")
                if return_response:
                    try:
                        return success, response.json()
                    except:
                        return success, response.text
                return success, {}
            else:
                error_msg = f"Expected {expected_status}, got {response.status_code}"
                try:
                    error_details = response.json()
                    error_msg += f" - {error_details}"
                except:
                    error_msg += f" - {response.text[:200]}"
                
                self.log_result(name, False, error_msg=error_msg)
                return False, {}

        except Exception as e:
            error_msg = f"Request failed: {str(e)}"
            self.log_result(name, False, error_msg=error_msg)
            return False, {}

    def test_root_endpoint(self):
        """Test root API endpoint"""
        return self.run_test("Root API Endpoint", "GET", "", 200)

    def test_company_crud(self):
        """Test complete Company CRUD operations"""
        print("\n" + "="*50)
        print("TESTING COMPANY CRUD OPERATIONS")
        print("="*50)
        
        # Test Create Company
        company_data = {
            "name": "Test Company Ltd",
            "address": "123 Test Street, Test City",
            "phone": "+62-21-1234567",
            "email": "test@company.com",
            "website": "https://testcompany.com",
            "motto": "Excellence in Every Service",
            "npwp": "12.345.678.9-012.000",
            "bank_name": "Bank Test Indonesia",
            "bank_account": "1234567890",
            "bank_account_name": "Test Company Ltd"
        }
        
        success, response = self.run_test(
            "Create Company", "POST", "companies", 201, 
            company_data, return_response=True
        )
        
        if success and response:
            self.created_company_id = response.get('id')
            print(f"   Created company ID: {self.created_company_id}")
        
        # Test Get All Companies
        self.run_test("Get All Companies", "GET", "companies", 200)
        
        # Test Get Single Company
        if self.created_company_id:
            self.run_test(
                "Get Single Company", "GET", 
                f"companies/{self.created_company_id}", 200
            )
            
            # Test Update Company
            update_data = {**company_data, "name": "Updated Test Company Ltd"}
            self.run_test(
                "Update Company", "PUT", 
                f"companies/{self.created_company_id}", 200, update_data
            )

    def test_item_crud(self):
        """Test complete Item CRUD operations"""
        print("\n" + "="*50)
        print("TESTING ITEM CRUD OPERATIONS")
        print("="*50)
        
        # Test Create Item
        item_data = {
            "name": "Test Product",
            "description": "A test product for testing purposes",
            "unit_price": 100000.0,
            "unit": "pcs"
        }
        
        success, response = self.run_test(
            "Create Item", "POST", "items", 201, 
            item_data, return_response=True
        )
        
        if success and response:
            self.created_item_id = response.get('id')
            print(f"   Created item ID: {self.created_item_id}")
        
        # Test Get All Items
        self.run_test("Get All Items", "GET", "items", 200)
        
        # Test Get Single Item
        if self.created_item_id:
            self.run_test(
                "Get Single Item", "GET", 
                f"items/{self.created_item_id}", 200
            )
            
            # Test Update Item
            update_data = {**item_data, "unit_price": 150000.0}
            self.run_test(
                "Update Item", "PUT", 
                f"items/{self.created_item_id}", 200, update_data
            )

    def test_invoice_crud(self):
        """Test complete Invoice CRUD operations"""
        print("\n" + "="*50)
        print("TESTING INVOICE CRUD OPERATIONS")
        print("="*50)
        
        if not self.created_company_id:
            print("❌ Cannot test invoices without a company. Skipping...")
            return
        
        # Test Create Invoice
        today = datetime.now().strftime('%Y-%m-%d')
        due_date = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
        
        invoice_data = {
            "invoice_number": f"INV-{datetime.now().strftime('%Y%m%d')}-001",
            "company_id": self.created_company_id,
            "client_name": "Test Client Corp",
            "client_address": "456 Client Street, Client City",
            "client_phone": "+62-21-9876543",
            "client_email": "client@testcorp.com",
            "date": today,
            "due_date": due_date,
            "items": [
                {
                    "item_id": self.created_item_id,
                    "name": "Test Product",
                    "description": "Test product description",
                    "quantity": 2.0,
                    "unit_price": 100000.0,
                    "unit": "pcs",
                    "total": 200000.0
                }
            ],
            "subtotal": 200000.0,
            "tax_rate": 11.0,
            "tax_amount": 22000.0,
            "discount_rate": 5.0,
            "discount_amount": 10000.0,
            "total": 212000.0,
            "currency": "IDR",
            "notes": "Test invoice notes",
            "template_id": "template1",
            "status": "draft"
        }
        
        success, response = self.run_test(
            "Create Invoice", "POST", "invoices", 201, 
            invoice_data, return_response=True
        )
        
        if success and response:
            self.created_invoice_id = response.get('id')
            print(f"   Created invoice ID: {self.created_invoice_id}")
        
        # Test Get All Invoices
        self.run_test("Get All Invoices", "GET", "invoices", 200)
        
        # Test Get Single Invoice
        if self.created_invoice_id:
            self.run_test(
                "Get Single Invoice", "GET", 
                f"invoices/{self.created_invoice_id}", 200
            )
            
            # Test Update Invoice
            update_data = {**invoice_data, "status": "sent"}
            self.run_test(
                "Update Invoice", "PUT", 
                f"invoices/{self.created_invoice_id}", 200, update_data
            )

    def test_quotation_crud(self):
        """Test complete Quotation CRUD operations"""
        print("\n" + "="*50)
        print("TESTING QUOTATION CRUD OPERATIONS")
        print("="*50)
        
        if not self.created_company_id:
            print("❌ Cannot test quotations without a company. Skipping...")
            return
        
        # Test Create Quotation
        today = datetime.now().strftime('%Y-%m-%d')
        valid_until = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
        
        quotation_data = {
            "quotation_number": f"QUO-{datetime.now().strftime('%Y%m%d')}-001",
            "company_id": self.created_company_id,
            "client_name": "Test Client Corp",
            "client_address": "456 Client Street, Client City",
            "client_phone": "+62-21-9876543",
            "client_email": "client@testcorp.com",
            "date": today,
            "valid_until": valid_until,
            "items": [
                {
                    "item_id": self.created_item_id,
                    "name": "Test Product",
                    "description": "Test product description",
                    "quantity": 3.0,
                    "unit_price": 100000.0,
                    "unit": "pcs",
                    "total": 300000.0
                }
            ],
            "subtotal": 300000.0,
            "tax_rate": 11.0,
            "tax_amount": 33000.0,
            "discount_rate": 0.0,
            "discount_amount": 0.0,
            "total": 333000.0,
            "currency": "USD",
            "notes": "Test quotation notes",
            "template_id": "template1",
            "status": "draft"
        }
        
        success, response = self.run_test(
            "Create Quotation", "POST", "quotations", 201, 
            quotation_data, return_response=True
        )
        
        if success and response:
            self.created_quotation_id = response.get('id')
            print(f"   Created quotation ID: {self.created_quotation_id}")
        
        # Test Get All Quotations
        self.run_test("Get All Quotations", "GET", "quotations", 200)
        
        # Test Get Single Quotation
        if self.created_quotation_id:
            self.run_test(
                "Get Single Quotation", "GET", 
                f"quotations/{self.created_quotation_id}", 200
            )
            
            # Test Update Quotation
            update_data = {**quotation_data, "status": "sent"}
            self.run_test(
                "Update Quotation", "PUT", 
                f"quotations/{self.created_quotation_id}", 200, update_data
            )

    def test_pdf_generation(self):
        """Test PDF generation for invoices and quotations"""
        print("\n" + "="*50)
        print("TESTING PDF GENERATION")
        print("="*50)
        
        # Test Invoice PDF
        if self.created_invoice_id:
            try:
                url = f"{self.api_url}/invoices/{self.created_invoice_id}/pdf"
                response = requests.get(url, timeout=30)
                
                if response.status_code == 200 and response.headers.get('content-type') == 'application/pdf':
                    self.log_result("Invoice PDF Generation", True, f"PDF size: {len(response.content)} bytes")
                else:
                    self.log_result("Invoice PDF Generation", False, error_msg=f"Status: {response.status_code}, Content-Type: {response.headers.get('content-type')}")
            except Exception as e:
                self.log_result("Invoice PDF Generation", False, error_msg=str(e))
        
        # Test Quotation PDF
        if self.created_quotation_id:
            try:
                url = f"{self.api_url}/quotations/{self.created_quotation_id}/pdf"
                response = requests.get(url, timeout=30)
                
                if response.status_code == 200 and response.headers.get('content-type') == 'application/pdf':
                    self.log_result("Quotation PDF Generation", True, f"PDF size: {len(response.content)} bytes")
                else:
                    self.log_result("Quotation PDF Generation", False, error_msg=f"Status: {response.status_code}, Content-Type: {response.headers.get('content-type')}")
            except Exception as e:
                self.log_result("Quotation PDF Generation", False, error_msg=str(e))

    def test_signature_upload(self):
        """Test signature image upload functionality"""
        print("\n" + "="*50)
        print("TESTING SIGNATURE UPLOAD")
        print("="*50)
        
        try:
            # Create a simple test image (1x1 pixel PNG)
            import base64
            # This is a minimal 1x1 pixel PNG image in base64
            test_image_b64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChAI9jU77mgAAAABJRU5ErkJggg=="
            test_image_bytes = base64.b64decode(test_image_b64)
            
            # Prepare multipart form data
            files = {'file': ('test_signature.png', test_image_bytes, 'image/png')}
            
            url = f"{self.api_url}/upload-signature"
            response = requests.post(url, files=files, timeout=30)
            
            if response.status_code == 200:
                response_data = response.json()
                if 'signature' in response_data:
                    self.uploaded_signature = response_data['signature']
                    self.log_result("Signature Upload", True, f"Signature uploaded successfully")
                else:
                    self.log_result("Signature Upload", False, error_msg="No signature field in response")
            else:
                error_msg = f"Status: {response.status_code}"
                try:
                    error_details = response.json()
                    error_msg += f" - {error_details}"
                except:
                    error_msg += f" - {response.text[:200]}"
                self.log_result("Signature Upload", False, error_msg=error_msg)
                
        except Exception as e:
            self.log_result("Signature Upload", False, error_msg=str(e))

    def test_letter_crud(self):
        """Test complete Letter CRUD operations"""
        print("\n" + "="*50)
        print("TESTING LETTER CRUD OPERATIONS")
        print("="*50)
        
        if not self.created_company_id:
            print("❌ Cannot test letters without a company. Skipping...")
            return
        
        # Test Create Letter with comprehensive data
        today = datetime.now().strftime('%Y-%m-%d')
        
        letter_data = {
            "letter_number": f"001/TEST-LETTER/{datetime.now().strftime('%m')}/{datetime.now().year}",
            "company_id": self.created_company_id,
            "date": today,
            "subject": "Penawaran Kerjasama Strategis",
            "letter_type": "cooperation",
            "recipient_name": "Bapak Direktur Utama",
            "recipient_position": "Direktur Utama",
            "recipient_address": "PT. Mitra Strategis Indonesia\nJl. Sudirman No. 123\nJakarta Pusat 10220",
            "content": "Dengan hormat,\n\nKami dari Test Company Ltd bermaksud untuk menawarkan kerjasama strategis dalam bidang teknologi informasi. Perusahaan kami telah berpengalaman lebih dari 10 tahun dalam memberikan solusi IT terpadu.\n\nAdapun bentuk kerjasama yang kami tawarkan meliputi:\n1. Pengembangan sistem informasi terintegrasi\n2. Konsultasi teknologi informasi\n3. Pelatihan SDM di bidang IT\n4. Maintenance dan support sistem\n\nKami yakin bahwa kerjasama ini akan memberikan manfaat yang optimal bagi kedua belah pihak. Untuk informasi lebih lanjut, kami siap melakukan presentasi dan diskusi lebih mendalam.\n\nDemikian surat penawaran ini kami sampaikan. Atas perhatian dan kerjasamanya, kami ucapkan terima kasih.",
            "attachments_count": 2,
            "cc_list": "1. Direktur Operasional\n2. Manager IT\n3. Kepala Bagian Procurement",
            "signatories": [
                {
                    "name": "John Doe",
                    "position": "Direktur Utama",
                    "signature_image": self.uploaded_signature if self.uploaded_signature else None
                },
                {
                    "name": "Jane Smith", 
                    "position": "Manager Business Development",
                    "signature_image": None
                }
            ]
        }
        
        success, response = self.run_test(
            "Create Letter", "POST", "letters", 201, 
            letter_data, return_response=True
        )
        
        if success and response:
            self.created_letter_id = response.get('id')
            print(f"   Created letter ID: {self.created_letter_id}")
        
        # Test Get All Letters
        self.run_test("Get All Letters", "GET", "letters", 200)
        
        # Test Get Single Letter
        if self.created_letter_id:
            self.run_test(
                "Get Single Letter", "GET", 
                f"letters/{self.created_letter_id}", 200
            )
            
            # Test Update Letter
            update_data = {**letter_data, "subject": "Updated: Penawaran Kerjasama Strategis"}
            self.run_test(
                "Update Letter", "PUT", 
                f"letters/{self.created_letter_id}", 200, update_data
            )

    def test_letter_types(self):
        """Test different letter types"""
        print("\n" + "="*50)
        print("TESTING DIFFERENT LETTER TYPES")
        print("="*50)
        
        if not self.created_company_id:
            print("❌ Cannot test letter types without a company. Skipping...")
            return
        
        letter_types = [
            {
                "type": "general",
                "subject": "Pemberitahuan Perubahan Alamat Kantor",
                "content": "Dengan hormat,\n\nKami memberitahukan bahwa mulai tanggal 1 Januari 2024, kantor pusat perusahaan kami akan pindah ke alamat baru.\n\nAlamat baru:\nJl. Gatot Subroto No. 456\nJakarta Selatan 12930\n\nSemua kegiatan operasional akan berjalan normal di lokasi baru tersebut."
            },
            {
                "type": "request", 
                "subject": "Permohonan Izin Penggunaan Fasilitas",
                "content": "Dengan hormat,\n\nSehubungan dengan rencana kegiatan pelatihan karyawan, kami bermaksud memohon izin penggunaan fasilitas aula perusahaan.\n\nDetail kegiatan:\n- Tanggal: 15-16 Februari 2024\n- Waktu: 08.00 - 17.00 WIB\n- Peserta: 50 orang\n- Jenis kegiatan: Pelatihan Leadership\n\nAtas perkenan dan kerjasamanya, kami ucapkan terima kasih."
            }
        ]
        
        for i, letter_type_data in enumerate(letter_types):
            letter_data = {
                "letter_number": f"00{i+2}/TEST-{letter_type_data['type'].upper()}/{datetime.now().strftime('%m')}/{datetime.now().year}",
                "company_id": self.created_company_id,
                "date": datetime.now().strftime('%Y-%m-%d'),
                "subject": letter_type_data['subject'],
                "letter_type": letter_type_data['type'],
                "recipient_name": f"Bapak/Ibu Penerima {letter_type_data['type'].title()}",
                "recipient_position": "Pimpinan",
                "recipient_address": "Alamat Penerima",
                "content": letter_type_data['content'],
                "attachments_count": 0,
                "cc_list": "",
                "signatories": [
                    {
                        "name": "Test Signatory",
                        "position": "Manager",
                        "signature_image": None
                    }
                ]
            }
            
            self.run_test(
                f"Create {letter_type_data['type'].title()} Letter", "POST", "letters", 201, letter_data
            )

    def test_letter_pdf_generation(self):
        """Test PDF generation for letters"""
        print("\n" + "="*50)
        print("TESTING LETTER PDF GENERATION")
        print("="*50)
        
        if self.created_letter_id:
            try:
                url = f"{self.api_url}/letters/{self.created_letter_id}/pdf"
                response = requests.get(url, timeout=30)
                
                if response.status_code == 200 and response.headers.get('content-type') == 'application/pdf':
                    self.log_result("Letter PDF Generation", True, f"PDF size: {len(response.content)} bytes")
                    
                    # Save PDF for manual verification if needed
                    # with open(f"/tmp/test_letter_{self.created_letter_id}.pdf", "wb") as f:
                    #     f.write(response.content)
                    
                else:
                    self.log_result("Letter PDF Generation", False, error_msg=f"Status: {response.status_code}, Content-Type: {response.headers.get('content-type')}")
            except Exception as e:
                self.log_result("Letter PDF Generation", False, error_msg=str(e))
        else:
            self.log_result("Letter PDF Generation", False, error_msg="No letter ID available for PDF generation test")

    def test_multi_currency(self):
        """Test multi-currency support"""
        print("\n" + "="*50)
        print("TESTING MULTI-CURRENCY SUPPORT")
        print("="*50)
        
        if not self.created_company_id:
            print("❌ Cannot test multi-currency without a company. Skipping...")
            return
        
        currencies = ["USD", "EUR", "SGD", "MYR"]
        
        for currency in currencies:
            invoice_data = {
                "invoice_number": f"INV-{currency}-{datetime.now().strftime('%Y%m%d')}-001",
                "company_id": self.created_company_id,
                "client_name": "Multi Currency Client",
                "client_address": "Currency Test Address",
                "date": datetime.now().strftime('%Y-%m-%d'),
                "items": [
                    {
                        "name": f"Test Product {currency}",
                        "description": f"Product in {currency}",
                        "quantity": 1.0,
                        "unit_price": 100.0,
                        "unit": "pcs",
                        "total": 100.0
                    }
                ],
                "subtotal": 100.0,
                "tax_rate": 0.0,
                "tax_amount": 0.0,
                "discount_rate": 0.0,
                "discount_amount": 0.0,
                "total": 100.0,
                "currency": currency,
                "status": "draft"
            }
            
            self.run_test(
                f"Create Invoice with {currency}", "POST", "invoices", 201, invoice_data
            )

    def cleanup_test_data(self):
        """Clean up created test data"""
        print("\n" + "="*50)
        print("CLEANING UP TEST DATA")
        print("="*50)
        
        # Delete Invoice
        if self.created_invoice_id:
            self.run_test(
                "Delete Invoice", "DELETE", 
                f"invoices/{self.created_invoice_id}", 200
            )
        
        # Delete Quotation
        if self.created_quotation_id:
            self.run_test(
                "Delete Quotation", "DELETE", 
                f"quotations/{self.created_quotation_id}", 200
            )
        
        # Delete Item
        if self.created_item_id:
            self.run_test(
                "Delete Item", "DELETE", 
                f"items/{self.created_item_id}", 200
            )
        
        # Delete Company
        if self.created_company_id:
            self.run_test(
                "Delete Company", "DELETE", 
                f"companies/{self.created_company_id}", 200
            )

    def run_all_tests(self):
        """Run all API tests"""
        print("🚀 Starting Invoice & Quotation API Tests")
        print(f"📍 Base URL: {self.base_url}")
        print(f"📍 API URL: {self.api_url}")
        
        # Test basic connectivity
        self.test_root_endpoint()
        
        # Test CRUD operations
        self.test_company_crud()
        self.test_item_crud()
        self.test_invoice_crud()
        self.test_quotation_crud()
        
        # Test advanced features
        self.test_pdf_generation()
        self.test_multi_currency()
        
        # Cleanup
        self.cleanup_test_data()
        
        # Print final results
        print("\n" + "="*60)
        print("FINAL TEST RESULTS")
        print("="*60)
        print(f"📊 Tests Run: {self.tests_run}")
        print(f"✅ Tests Passed: {self.tests_passed}")
        print(f"❌ Tests Failed: {self.tests_run - self.tests_passed}")
        print(f"📈 Success Rate: {(self.tests_passed/self.tests_run*100):.1f}%")
        
        # Print failed tests
        failed_tests = [r for r in self.test_results if not r['success']]
        if failed_tests:
            print(f"\n❌ Failed Tests ({len(failed_tests)}):")
            for test in failed_tests:
                print(f"   • {test['test']}: {test['error']}")
        
        return self.tests_passed == self.tests_run

def main():
    """Main test execution"""
    tester = InvoiceQuotationAPITester()
    
    try:
        success = tester.run_all_tests()
        return 0 if success else 1
    except KeyboardInterrupt:
        print("\n⚠️  Tests interrupted by user")
        return 1
    except Exception as e:
        print(f"\n💥 Unexpected error: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())