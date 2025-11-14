from fastapi import FastAPI, APIRouter, HTTPException, UploadFile, File
from fastapi.responses import StreamingResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
import uuid
from datetime import datetime, timezone
import base64
import io
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER
from reportlab.pdfgen import canvas
from PIL import Image

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Define Models
class Company(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    address: str = ""
    phone: str = ""
    email: str = ""
    website: str = ""
    motto: str = ""
    npwp: str = ""
    bank_name: str = ""
    bank_account: str = ""
    bank_account_name: str = ""
    logo: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class CompanyCreate(BaseModel):
    name: str
    address: str = ""
    phone: str = ""
    email: str = ""
    website: str = ""
    motto: str = ""
    npwp: str = ""
    bank_name: str = ""
    bank_account: str = ""
    bank_account_name: str = ""
    logo: Optional[str] = None

class Item(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str = ""
    unit_price: float
    unit: str = "pcs"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ItemCreate(BaseModel):
    name: str
    description: str = ""
    unit_price: float
    unit: str = "pcs"

class InvoiceItem(BaseModel):
    item_id: Optional[str] = None
    name: str
    description: str = ""
    quantity: float
    unit_price: float
    unit: str = "pcs"
    total: float

class Invoice(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    invoice_number: str
    company_id: str
    client_name: str
    client_address: str = ""
    client_phone: str = ""
    client_email: str = ""
    date: str
    due_date: str = ""
    items: List[InvoiceItem]
    subtotal: float
    tax_rate: float = 0
    tax_amount: float = 0
    discount_rate: float = 0
    discount_amount: float = 0
    total: float
    currency: str = "IDR"
    notes: str = ""
    template_id: str = "template1"
    status: str = "draft"
    signature_name: str = ""
    signature_position: str = ""
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class InvoiceCreate(BaseModel):
    invoice_number: str
    company_id: str
    client_name: str
    client_address: str = ""
    client_phone: str = ""
    client_email: str = ""
    date: str
    due_date: str = ""
    items: List[InvoiceItem]
    subtotal: float
    tax_rate: float = 0
    tax_amount: float = 0
    discount_rate: float = 0
    discount_amount: float = 0
    total: float
    currency: str = "IDR"
    notes: str = ""
    template_id: str = "template1"
    status: str = "draft"
    signature_name: str = ""
    signature_position: str = ""

class Quotation(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    quotation_number: str
    company_id: str
    client_name: str
    client_address: str = ""
    client_phone: str = ""
    client_email: str = ""
    date: str
    valid_until: str = ""
    items: List[InvoiceItem]
    subtotal: float
    tax_rate: float = 0
    tax_amount: float = 0
    discount_rate: float = 0
    discount_amount: float = 0
    total: float
    currency: str = "IDR"
    notes: str = ""
    template_id: str = "template1"
    status: str = "draft"
    signature_name: str = ""
    signature_position: str = ""
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class QuotationCreate(BaseModel):
    quotation_number: str
    company_id: str
    client_name: str
    client_address: str = ""
    client_phone: str = ""
    client_email: str = ""
    date: str
    valid_until: str = ""
    items: List[InvoiceItem]
    subtotal: float
    tax_rate: float = 0
    tax_amount: float = 0
    discount_rate: float = 0
    discount_amount: float = 0
    total: float
    currency: str = "IDR"
    notes: str = ""
    template_id: str = "template1"
    status: str = "draft"
    signature_name: str = ""
    signature_position: str = ""

class Signatory(BaseModel):
    name: str
    position: str
    signature_image: Optional[str] = None

class Letter(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    letter_number: str
    company_id: str
    date: str
    subject: str
    letter_type: str = "general"  # general, cooperation, request
    recipient_name: str
    recipient_position: str = ""
    recipient_address: str = ""
    content: str
    attachments_count: int = 0
    cc_list: str = ""
    signatories: List[Signatory] = []
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class LetterCreate(BaseModel):
    letter_number: str
    company_id: str
    date: str
    subject: str
    letter_type: str = "general"
    recipient_name: str
    recipient_position: str = ""
    recipient_address: str = ""
    content: str
    attachments_count: int = 0
    cc_list: str = ""
    signatories: List[Signatory] = []

# Routes
@api_router.get("/")
async def root():
    return {"message": "Invoice & Quotation API"}

# Company Routes
@api_router.post("/companies", response_model=Company, status_code=201)
async def create_company(input: CompanyCreate):
    company_dict = input.model_dump()
    company = Company(**company_dict)
    doc = company.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    await db.companies.insert_one(doc)
    return company

@api_router.get("/companies", response_model=List[Company])
async def get_companies():
    companies = await db.companies.find({}, {"_id": 0}).to_list(1000)
    for company in companies:
        if isinstance(company['created_at'], str):
            company['created_at'] = datetime.fromisoformat(company['created_at'])
    return companies

@api_router.get("/companies/{company_id}", response_model=Company)
async def get_company(company_id: str):
    company = await db.companies.find_one({"id": company_id}, {"_id": 0})
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    if isinstance(company['created_at'], str):
        company['created_at'] = datetime.fromisoformat(company['created_at'])
    return company

@api_router.put("/companies/{company_id}", response_model=Company)
async def update_company(company_id: str, input: CompanyCreate):
    company = await db.companies.find_one({"id": company_id}, {"_id": 0})
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    update_dict = input.model_dump()
    await db.companies.update_one({"id": company_id}, {"$set": update_dict})
    
    updated_company = await db.companies.find_one({"id": company_id}, {"_id": 0})
    if isinstance(updated_company['created_at'], str):
        updated_company['created_at'] = datetime.fromisoformat(updated_company['created_at'])
    return updated_company

@api_router.delete("/companies/{company_id}")
async def delete_company(company_id: str):
    result = await db.companies.delete_one({"id": company_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Company not found")
    return {"message": "Company deleted successfully"}

# Item Routes
@api_router.post("/items", response_model=Item, status_code=201)
async def create_item(input: ItemCreate):
    item_dict = input.model_dump()
    item = Item(**item_dict)
    doc = item.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    await db.items.insert_one(doc)
    return item

@api_router.get("/items", response_model=List[Item])
async def get_items():
    items = await db.items.find({}, {"_id": 0}).to_list(1000)
    for item in items:
        if isinstance(item['created_at'], str):
            item['created_at'] = datetime.fromisoformat(item['created_at'])
    return items

@api_router.get("/items/{item_id}", response_model=Item)
async def get_item(item_id: str):
    item = await db.items.find_one({"id": item_id}, {"_id": 0})
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    if isinstance(item['created_at'], str):
        item['created_at'] = datetime.fromisoformat(item['created_at'])
    return item

@api_router.put("/items/{item_id}", response_model=Item)
async def update_item(item_id: str, input: ItemCreate):
    item = await db.items.find_one({"id": item_id}, {"_id": 0})
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    update_dict = input.model_dump()
    await db.items.update_one({"id": item_id}, {"$set": update_dict})
    
    updated_item = await db.items.find_one({"id": item_id}, {"_id": 0})
    if isinstance(updated_item['created_at'], str):
        updated_item['created_at'] = datetime.fromisoformat(updated_item['created_at'])
    return updated_item

@api_router.delete("/items/{item_id}")
async def delete_item(item_id: str):
    result = await db.items.delete_one({"id": item_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"message": "Item deleted successfully"}

# Invoice Routes
@api_router.post("/invoices", response_model=Invoice, status_code=201)
async def create_invoice(input: InvoiceCreate):
    invoice_dict = input.model_dump()
    invoice = Invoice(**invoice_dict)
    doc = invoice.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    await db.invoices.insert_one(doc)
    return invoice

@api_router.get("/invoices", response_model=List[Invoice])
async def get_invoices():
    invoices = await db.invoices.find({}, {"_id": 0}).to_list(1000)
    for invoice in invoices:
        if isinstance(invoice['created_at'], str):
            invoice['created_at'] = datetime.fromisoformat(invoice['created_at'])
    return invoices

@api_router.get("/invoices/{invoice_id}", response_model=Invoice)
async def get_invoice(invoice_id: str):
    invoice = await db.invoices.find_one({"id": invoice_id}, {"_id": 0})
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    if isinstance(invoice['created_at'], str):
        invoice['created_at'] = datetime.fromisoformat(invoice['created_at'])
    return invoice

@api_router.put("/invoices/{invoice_id}", response_model=Invoice)
async def update_invoice(invoice_id: str, input: InvoiceCreate):
    invoice = await db.invoices.find_one({"id": invoice_id}, {"_id": 0})
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    update_dict = input.model_dump()
    await db.invoices.update_one({"id": invoice_id}, {"$set": update_dict})
    
    updated_invoice = await db.invoices.find_one({"id": invoice_id}, {"_id": 0})
    if isinstance(updated_invoice['created_at'], str):
        updated_invoice['created_at'] = datetime.fromisoformat(updated_invoice['created_at'])
    return updated_invoice

@api_router.delete("/invoices/{invoice_id}")
async def delete_invoice(invoice_id: str):
    result = await db.invoices.delete_one({"id": invoice_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return {"message": "Invoice deleted successfully"}

# Quotation Routes
@api_router.post("/quotations", response_model=Quotation, status_code=201)
async def create_quotation(input: QuotationCreate):
    quotation_dict = input.model_dump()
    quotation = Quotation(**quotation_dict)
    doc = quotation.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    await db.quotations.insert_one(doc)
    return quotation

@api_router.get("/quotations", response_model=List[Quotation])
async def get_quotations():
    quotations = await db.quotations.find({}, {"_id": 0}).to_list(1000)
    for quotation in quotations:
        if isinstance(quotation['created_at'], str):
            quotation['created_at'] = datetime.fromisoformat(quotation['created_at'])
    return quotations

@api_router.get("/quotations/{quotation_id}", response_model=Quotation)
async def get_quotation(quotation_id: str):
    quotation = await db.quotations.find_one({"id": quotation_id}, {"_id": 0})
    if not quotation:
        raise HTTPException(status_code=404, detail="Quotation not found")
    if isinstance(quotation['created_at'], str):
        quotation['created_at'] = datetime.fromisoformat(quotation['created_at'])
    return quotation

@api_router.put("/quotations/{quotation_id}", response_model=Quotation)
async def update_quotation(quotation_id: str, input: QuotationCreate):
    quotation = await db.quotations.find_one({"id": quotation_id}, {"_id": 0})
    if not quotation:
        raise HTTPException(status_code=404, detail="Quotation not found")
    
    update_dict = input.model_dump()
    await db.quotations.update_one({"id": quotation_id}, {"$set": update_dict})
    
    updated_quotation = await db.quotations.find_one({"id": quotation_id}, {"_id": 0})
    if isinstance(updated_quotation['created_at'], str):
        updated_quotation['created_at'] = datetime.fromisoformat(updated_quotation['created_at'])
    return updated_quotation

@api_router.delete("/quotations/{quotation_id}")
async def delete_quotation(quotation_id: str):
    result = await db.quotations.delete_one({"id": quotation_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Quotation not found")
    return {"message": "Quotation deleted successfully"}

# Letter Routes
@api_router.get("/letters")
async def get_letters():
    letters = await db.letters.find().to_list(length=None)
    return [Letter(**letter) for letter in letters]

@api_router.post("/letters", status_code=201)
async def create_letter(letter: LetterCreate):
    letter_dict = letter.dict()
    letter_dict["id"] = str(uuid.uuid4())
    letter_dict["created_at"] = datetime.now(timezone.utc).isoformat()
    letter_dict["signatories"] = [sig.dict() for sig in letter.signatories]
    await db.letters.insert_one(letter_dict)
    return Letter(**letter_dict)

@api_router.get("/letters/{letter_id}")
async def get_letter(letter_id: str):
    letter = await db.letters.find_one({"id": letter_id})
    if not letter:
        raise HTTPException(status_code=404, detail="Letter not found")
    return Letter(**letter)

@api_router.put("/letters/{letter_id}")
async def update_letter(letter_id: str, letter: LetterCreate):
    letter_dict = letter.dict()
    letter_dict["signatories"] = [sig.dict() for sig in letter.signatories]
    result = await db.letters.update_one(
        {"id": letter_id},
        {"$set": letter_dict}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Letter not found")
    
    updated_letter = await db.letters.find_one({"id": letter_id})
    return Letter(**updated_letter)

@api_router.delete("/letters/{letter_id}")
async def delete_letter(letter_id: str):
    result = await db.letters.delete_one({"id": letter_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Letter not found")
    return {"message": "Letter deleted successfully"}

# Signature Upload Route
@api_router.post("/upload-signature")
async def upload_signature(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        
        # Validate image
        try:
            img = Image.open(io.BytesIO(contents))
            img.verify()
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid image file")
        
        # Convert to base64
        base64_image = base64.b64encode(contents).decode('utf-8')
        mime_type = file.content_type or 'image/png'
        data_uri = f"data:{mime_type};base64,{base64_image}"
        
        return {"signature": data_uri}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# PDF Generation Routes
def format_currency(amount: float, currency: str) -> str:
    if currency == "IDR":
        return f"Rp {amount:,.0f}"
    elif currency == "USD":
        return f"${amount:,.2f}"
    elif currency == "EUR":
        return f"€{amount:,.2f}"
    else:
        return f"{currency} {amount:,.2f}"

@api_router.get("/invoices/{invoice_id}/pdf")
async def generate_invoice_pdf(invoice_id: str):
    invoice = await db.invoices.find_one({"id": invoice_id}, {"_id": 0})
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    company = await db.companies.find_one({"id": invoice['company_id']}, {"_id": 0})
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=50, leftMargin=50, topMargin=50, bottomMargin=50)
    
    story = []
    styles = getSampleStyleSheet()
    
    # Header
    header_style = ParagraphStyle('header', parent=styles['Heading1'], fontSize=24, textColor=colors.HexColor('#1e40af'), alignment=TA_CENTER)
    story.append(Paragraph("INVOICE", header_style))
    story.append(Spacer(1, 20))
    
    # Company Info
    company_style = ParagraphStyle('company', parent=styles['Normal'], fontSize=10, alignment=TA_LEFT)
    story.append(Paragraph(f"<b>{company['name']}</b>", company_style))
    story.append(Paragraph(company['address'], company_style))
    story.append(Paragraph(f"Phone: {company['phone']} | Email: {company['email']}", company_style))
    if company.get('npwp'):
        story.append(Paragraph(f"NPWP: {company['npwp']}", company_style))
    story.append(Spacer(1, 20))
    
    # Invoice Info
    info_data = [
        ["Invoice Number:", invoice['invoice_number'], "Date:", invoice['date']],
        ["Client:", invoice['client_name'], "Due Date:", invoice.get('due_date', '-')],
    ]
    info_table = Table(info_data, colWidths=[100, 200, 80, 120])
    info_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 20))
    
    # Items Table
    items_data = [['Item', 'Description', 'Qty', 'Unit Price', 'Total']]
    for item in invoice['items']:
        items_data.append([
            item['name'],
            item['description'],
            f"{item['quantity']} {item['unit']}",
            format_currency(item['unit_price'], invoice['currency']),
            format_currency(item['total'], invoice['currency'])
        ])
    
    items_table = Table(items_data, colWidths=[120, 150, 60, 80, 90])
    items_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e40af')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (2, 0), (-1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.whitesmoke, colors.white]),
    ]))
    story.append(items_table)
    story.append(Spacer(1, 20))
    
    # Summary
    summary_data = [
        ['Subtotal:', format_currency(invoice['subtotal'], invoice['currency'])],
    ]
    if invoice.get('discount_amount', 0) > 0:
        summary_data.append([f"Discount ({invoice.get('discount_rate', 0)}%):", format_currency(invoice['discount_amount'], invoice['currency'])])
    if invoice.get('tax_amount', 0) > 0:
        summary_data.append([f"Tax ({invoice.get('tax_rate', 0)}%):", format_currency(invoice['tax_amount'], invoice['currency'])])
    summary_data.append(['Total:', format_currency(invoice['total'], invoice['currency'])])
    
    summary_table = Table(summary_data, colWidths=[350, 150])
    summary_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LINEABOVE', (0, -1), (-1, -1), 2, colors.HexColor('#1e40af')),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, -1), (-1, -1), 12),
    ]))
    story.append(summary_table)
    
    if invoice.get('notes'):
        story.append(Spacer(1, 20))
        story.append(Paragraph(f"<b>Notes:</b>", styles['Normal']))
        story.append(Paragraph(invoice['notes'], styles['Normal']))
    
    if company.get('bank_name'):
        story.append(Spacer(1, 30))
        story.append(Paragraph("<b>Payment Details:</b>", styles['Normal']))
        story.append(Paragraph(f"Bank: {company['bank_name']}", styles['Normal']))
        story.append(Paragraph(f"Account: {company['bank_account']}", styles['Normal']))
        story.append(Paragraph(f"Account Name: {company['bank_account_name']}", styles['Normal']))
    
    # Signature section
    if invoice.get('signature_name') or invoice.get('signature_position'):
        story.append(Spacer(1, 40))
        signature_style = ParagraphStyle('signature', parent=styles['Normal'], fontSize=10, alignment=TA_RIGHT)
        story.append(Paragraph("<b>Authorized Signature:</b>", signature_style))
        story.append(Spacer(1, 40))
        if invoice.get('signature_name'):
            story.append(Paragraph(f"<b>{invoice['signature_name']}</b>", signature_style))
        if invoice.get('signature_position'):
            story.append(Paragraph(invoice['signature_position'], signature_style))
    
    doc.build(story)
    buffer.seek(0)
    
    return StreamingResponse(buffer, media_type="application/pdf", headers={
        "Content-Disposition": f"attachment; filename=invoice_{invoice['invoice_number']}.pdf"
    })

@api_router.get("/quotations/{quotation_id}/pdf")
async def generate_quotation_pdf(quotation_id: str):
    quotation = await db.quotations.find_one({"id": quotation_id}, {"_id": 0})
    if not quotation:
        raise HTTPException(status_code=404, detail="Quotation not found")
    
    company = await db.companies.find_one({"id": quotation['company_id']}, {"_id": 0})
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=50, leftMargin=50, topMargin=50, bottomMargin=50)
    
    story = []
    styles = getSampleStyleSheet()
    
    # Header
    header_style = ParagraphStyle('header', parent=styles['Heading1'], fontSize=24, textColor=colors.HexColor('#059669'), alignment=TA_CENTER)
    story.append(Paragraph("QUOTATION", header_style))
    story.append(Spacer(1, 20))
    
    # Company Info
    company_style = ParagraphStyle('company', parent=styles['Normal'], fontSize=10, alignment=TA_LEFT)
    story.append(Paragraph(f"<b>{company['name']}</b>", company_style))
    story.append(Paragraph(company['address'], company_style))
    story.append(Paragraph(f"Phone: {company['phone']} | Email: {company['email']}", company_style))
    if company.get('npwp'):
        story.append(Paragraph(f"NPWP: {company['npwp']}", company_style))
    story.append(Spacer(1, 20))
    
    # Quotation Info
    info_data = [
        ["Quotation Number:", quotation['quotation_number'], "Date:", quotation['date']],
        ["Client:", quotation['client_name'], "Valid Until:", quotation.get('valid_until', '-')],
    ]
    info_table = Table(info_data, colWidths=[120, 180, 80, 120])
    info_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 20))
    
    # Items Table
    items_data = [['Item', 'Description', 'Qty', 'Unit Price', 'Total']]
    for item in quotation['items']:
        items_data.append([
            item['name'],
            item['description'],
            f"{item['quantity']} {item['unit']}",
            format_currency(item['unit_price'], quotation['currency']),
            format_currency(item['total'], quotation['currency'])
        ])
    
    items_table = Table(items_data, colWidths=[120, 150, 60, 80, 90])
    items_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#059669')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (2, 0), (-1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.whitesmoke, colors.white]),
    ]))
    story.append(items_table)
    story.append(Spacer(1, 20))
    
    # Summary
    summary_data = [
        ['Subtotal:', format_currency(quotation['subtotal'], quotation['currency'])],
    ]
    if quotation.get('discount_amount', 0) > 0:
        summary_data.append([f"Discount ({quotation.get('discount_rate', 0)}%):", format_currency(quotation['discount_amount'], quotation['currency'])])
    if quotation.get('tax_amount', 0) > 0:
        summary_data.append([f"Tax ({quotation.get('tax_rate', 0)}%):", format_currency(quotation['tax_amount'], quotation['currency'])])
    summary_data.append(['Total:', format_currency(quotation['total'], quotation['currency'])])
    
    summary_table = Table(summary_data, colWidths=[350, 150])
    summary_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LINEABOVE', (0, -1), (-1, -1), 2, colors.HexColor('#059669')),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, -1), (-1, -1), 12),
    ]))
    story.append(summary_table)
    
    if quotation.get('notes'):
        story.append(Spacer(1, 20))
        story.append(Paragraph(f"<b>Notes:</b>", styles['Normal']))
        story.append(Paragraph(quotation['notes'], styles['Normal']))
    
    if company.get('bank_name'):
        story.append(Spacer(1, 30))
        story.append(Paragraph("<b>Payment Details:</b>", styles['Normal']))
        story.append(Paragraph(f"Bank: {company['bank_name']}", styles['Normal']))
        story.append(Paragraph(f"Account: {company['bank_account']}", styles['Normal']))
        story.append(Paragraph(f"Account Name: {company['bank_account_name']}", styles['Normal']))
    
    # Signature section
    if quotation.get('signature_name') or quotation.get('signature_position'):
        story.append(Spacer(1, 40))
        signature_style = ParagraphStyle('signature', parent=styles['Normal'], fontSize=10, alignment=TA_RIGHT)
        story.append(Paragraph("<b>Authorized Signature:</b>", signature_style))
        story.append(Spacer(1, 40))
        if quotation.get('signature_name'):
            story.append(Paragraph(f"<b>{quotation['signature_name']}</b>", signature_style))
        if quotation.get('signature_position'):
            story.append(Paragraph(quotation['signature_position'], signature_style))
    
    doc.build(story)
    buffer.seek(0)
    
    return StreamingResponse(buffer, media_type="application/pdf", headers={
        "Content-Disposition": f"attachment; filename=quotation_{quotation['quotation_number']}.pdf"
    })

# Letter PDF Generation
@api_router.get("/letters/{letter_id}/pdf")
async def generate_letter_pdf(letter_id: str):
    letter = await db.letters.find_one({"id": letter_id})
    if not letter:
        raise HTTPException(status_code=404, detail="Letter not found")
    
    company = await db.companies.find_one({"id": letter['company_id']})
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.5*inch, bottomMargin=0.5*inch)
    story = []
    styles = getSampleStyleSheet()
    
    # Company Header with Logo (Kop Surat)
    header_data = []
    if company.get('logo'):
        try:
            logo_data = company['logo'].split(',')[1] if ',' in company['logo'] else company['logo']
            logo_bytes = base64.b64decode(logo_data)
            logo_img = Image.open(io.BytesIO(logo_bytes))
            
            # Resize logo
            max_width, max_height = 60, 60
            logo_img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
            
            logo_buffer = io.BytesIO()
            logo_img.save(logo_buffer, format='PNG')
            logo_buffer.seek(0)
            
            logo = RLImage(logo_buffer, width=logo_img.width, height=logo_img.height)
            
            company_info = f"""<b>{company['name']}</b><br/>
            {company.get('motto', '')}<br/>
            {company.get('address', '')}<br/>
            Tel: {company.get('phone', '')} | Email: {company.get('email', '')}<br/>
            Website: {company.get('website', '')}"""
            
            header_data = [[logo, Paragraph(company_info, styles['Normal'])]]
        except:
            pass
    
    if not header_data:
        company_style = ParagraphStyle('company', parent=styles['Normal'], fontSize=12, alignment=TA_CENTER)
        story.append(Paragraph(f"<b>{company['name']}</b>", company_style))
        if company.get('motto'):
            story.append(Paragraph(company['motto'], company_style))
        story.append(Paragraph(company.get('address', ''), company_style))
        story.append(Paragraph(f"Tel: {company.get('phone', '')} | Email: {company.get('email', '')}", company_style))
        if company.get('website'):
            story.append(Paragraph(f"Website: {company['website']}", company_style))
    else:
        header_table = Table(header_data, colWidths=[80, 450])
        header_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('ALIGN', (0, 0), (0, 0), 'CENTER'),
        ]))
        story.append(header_table)
    
    # Line separator
    story.append(Spacer(1, 10))
    separator_table = Table([['']], colWidths=[500])
    separator_table.setStyle(TableStyle([
        ('LINEABOVE', (0, 0), (-1, 0), 2, colors.HexColor('#000000')),
        ('LINEBELOW', (0, 0), (-1, 0), 1, colors.HexColor('#000000')),
    ]))
    story.append(separator_table)
    story.append(Spacer(1, 20))
    
    # Letter Number and Date
    letter_info_style = ParagraphStyle('letterinfo', parent=styles['Normal'], fontSize=10, alignment=TA_LEFT)
    story.append(Paragraph(f"Nomor: {letter['letter_number']}", letter_info_style))
    story.append(Paragraph(f"Tanggal: {letter['date']}", letter_info_style))
    
    if letter.get('attachments_count', 0) > 0:
        story.append(Paragraph(f"Lampiran: {letter['attachments_count']} berkas", letter_info_style))
    
    story.append(Paragraph(f"Perihal: <b>{letter['subject']}</b>", letter_info_style))
    story.append(Spacer(1, 20))
    
    # Recipient
    story.append(Paragraph("Kepada Yth,", styles['Normal']))
    story.append(Paragraph(f"<b>{letter['recipient_name']}</b>", styles['Normal']))
    if letter.get('recipient_position'):
        story.append(Paragraph(letter['recipient_position'], styles['Normal']))
    if letter.get('recipient_address'):
        story.append(Paragraph(letter['recipient_address'], styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Greeting based on letter type
    if letter['letter_type'] == 'general':
        story.append(Paragraph("Dengan hormat,", styles['Normal']))
    elif letter['letter_type'] == 'cooperation':
        story.append(Paragraph("Dengan hormat,", styles['Normal']))
    elif letter['letter_type'] == 'request':
        story.append(Paragraph("Dengan hormat,", styles['Normal']))
    
    story.append(Spacer(1, 12))
    
    # Letter Content
    content_style = ParagraphStyle('content', parent=styles['Normal'], fontSize=11, alignment=TA_JUSTIFY, leading=16)
    
    # Split content by paragraphs
    paragraphs = letter['content'].split('\n')
    for para in paragraphs:
        if para.strip():
            story.append(Paragraph(para.strip(), content_style))
            story.append(Spacer(1, 8))
    
    story.append(Spacer(1, 12))
    
    # Closing based on letter type
    if letter['letter_type'] == 'general':
        story.append(Paragraph("Demikian surat ini kami sampaikan. Atas perhatian dan kerjasamanya, kami ucapkan terima kasih.", styles['Normal']))
    elif letter['letter_type'] == 'cooperation':
        story.append(Paragraph("Demikian surat penawaran kerjasama ini kami sampaikan. Besar harapan kami dapat menjalin kerjasama yang baik dengan perusahaan Bapak/Ibu.", styles['Normal']))
    elif letter['letter_type'] == 'request':
        story.append(Paragraph("Demikian permohonan ini kami sampaikan, atas perhatian dan perkenannya kami ucapkan terima kasih.", styles['Normal']))
    
    story.append(Spacer(1, 30))
    
    # Signatories
    if letter.get('signatories') and len(letter['signatories']) > 0:
        sig_data = []
        sig_widths = []
        
        num_sigs = len(letter['signatories'])
        col_width = 500 // num_sigs
        
        for sig in letter['signatories']:
            sig_content = []
            sig_style = ParagraphStyle('sig', parent=styles['Normal'], fontSize=10, alignment=TA_CENTER)
            
            sig_content.append(Paragraph(sig.get('position', ''), sig_style))
            sig_content.append(Spacer(1, 5))
            
            # Add signature image if available
            if sig.get('signature_image'):
                try:
                    sig_img_data = sig['signature_image'].split(',')[1] if ',' in sig['signature_image'] else sig['signature_image']
                    sig_img_bytes = base64.b64decode(sig_img_data)
                    sig_img_pil = Image.open(io.BytesIO(sig_img_bytes))
                    
                    # Resize signature
                    max_sig_width, max_sig_height = 80, 40
                    sig_img_pil.thumbnail((max_sig_width, max_sig_height), Image.Resampling.LANCZOS)
                    
                    sig_img_buffer = io.BytesIO()
                    sig_img_pil.save(sig_img_buffer, format='PNG')
                    sig_img_buffer.seek(0)
                    
                    sig_image = RLImage(sig_img_buffer, width=sig_img_pil.width, height=sig_img_pil.height)
                    sig_content.append(sig_image)
                except:
                    sig_content.append(Spacer(1, 40))
            else:
                sig_content.append(Spacer(1, 40))
            
            sig_content.append(Spacer(1, 5))
            sig_content.append(Paragraph(f"<b>{sig.get('name', '')}</b>", sig_style))
            
            sig_data.append(sig_content)
            sig_widths.append(col_width)
        
        # Create signature table
        sig_table = Table([sig_data], colWidths=sig_widths)
        sig_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ]))
        story.append(sig_table)
    
    # CC List
    if letter.get('cc_list'):
        story.append(Spacer(1, 30))
        story.append(Paragraph("<b>Tembusan:</b>", styles['Normal']))
        cc_items = letter['cc_list'].split('\n')
        for cc in cc_items:
            if cc.strip():
                story.append(Paragraph(f"- {cc.strip()}", styles['Normal']))
    
    doc.build(story)
    buffer.seek(0)
    
    return StreamingResponse(buffer, media_type="application/pdf", headers={
        "Content-Disposition": f"attachment; filename=letter_{letter['letter_number'].replace('/', '_')}.pdf"
    })

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()