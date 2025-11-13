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

# Routes
@api_router.get("/")
async def root():
    return {"message": "Invoice & Quotation API"}

# Company Routes
@api_router.post("/companies", response_model=Company)
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
@api_router.post("/items", response_model=Item)
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
@api_router.post("/invoices", response_model=Invoice)
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
@api_router.post("/quotations", response_model=Quotation)
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
    summary_data.append(['<b>Total:</b>', f"<b>{format_currency(invoice['total'], invoice['currency'])}</b>"])
    
    summary_table = Table(summary_data, colWidths=[350, 150])
    summary_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LINEABOVE', (0, -1), (-1, -1), 2, colors.HexColor('#1e40af')),
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
    summary_data.append(['<b>Total:</b>', f"<b>{format_currency(quotation['total'], quotation['currency'])}</b>"])
    
    summary_table = Table(summary_data, colWidths=[350, 150])
    summary_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LINEABOVE', (0, -1), (-1, -1), 2, colors.HexColor('#059669')),
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
    
    doc.build(story)
    buffer.seek(0)
    
    return StreamingResponse(buffer, media_type="application/pdf", headers={
        "Content-Disposition": f"attachment; filename=quotation_{quotation['quotation_number']}.pdf"
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