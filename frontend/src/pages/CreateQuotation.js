import React, { useState, useEffect } from "react";
import axios from "axios";
import { API } from "../App";
import { useNavigate } from "react-router-dom";
import { Plus, Trash2, ArrowLeft } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { toast } from "sonner";

const CreateQuotation = () => {
  const navigate = useNavigate();
  const [companies, setCompanies] = useState([]);
  const [items, setItems] = useState([]);
  const [formData, setFormData] = useState({
    quotation_number: "",
    company_id: "",
    client_name: "",
    client_address: "",
    client_phone: "",
    client_email: "",
    date: new Date().toISOString().split('T')[0],
    valid_until: "",
    currency: "IDR",
    tax_rate: 0,
    discount_rate: 0,
    notes: "",
    template_id: "template1",
    status: "draft",
  });
  const [invoiceItems, setInvoiceItems] = useState([{
    item_id: "",
    name: "",
    description: "",
    quantity: 1,
    unit_price: 0,
    unit: "pcs",
    total: 0,
  }]);

  useEffect(() => {
    fetchCompanies();
    fetchItems();
  }, []);

  const fetchCompanies = async () => {
    try {
      const response = await axios.get(`${API}/companies`);
      setCompanies(response.data);
    } catch (error) {
      console.error("Error fetching companies:", error);
    }
  };

  const fetchItems = async () => {
    try {
      const response = await axios.get(`${API}/items`);
      setItems(response.data);
    } catch (error) {
      console.error("Error fetching items:", error);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
  };

  const handleSelectChange = (name, value) => {
    setFormData({ ...formData, [name]: value });
  };

  const handleItemChange = (index, field, value) => {
    const newItems = [...invoiceItems];
    newItems[index][field] = value;
    
    // Auto calculate total
    if (field === 'quantity' || field === 'unit_price') {
      newItems[index].total = parseFloat(newItems[index].quantity || 0) * parseFloat(newItems[index].unit_price || 0);
    }
    
    setInvoiceItems(newItems);
  };

  const handleSelectItem = (index, itemId) => {
    const selectedItem = items.find(item => item.id === itemId);
    if (selectedItem) {
      const newItems = [...invoiceItems];
      newItems[index] = {
        ...newItems[index],
        item_id: selectedItem.id,
        name: selectedItem.name,
        description: selectedItem.description,
        unit_price: selectedItem.unit_price,
        unit: selectedItem.unit,
        total: newItems[index].quantity * selectedItem.unit_price,
      };
      setInvoiceItems(newItems);
    }
  };

  const addItem = () => {
    setInvoiceItems([...invoiceItems, {
      item_id: "",
      name: "",
      description: "",
      quantity: 1,
      unit_price: 0,
      unit: "pcs",
      total: 0,
    }]);
  };

  const removeItem = (index) => {
    if (quotationItems.length > 1) {
      const newItems = quotationItems.filter((_, i) => i !== index);
      setInvoiceItems(newItems);
    }
  };

  const calculateSubtotal = () => {
    return quotationItems.reduce((sum, item) => sum + (item.total || 0), 0);
  };

  const calculateDiscount = () => {
    return calculateSubtotal() * (parseFloat(formData.discount_rate || 0) / 100);
  };

  const calculateTax = () => {
    const afterDiscount = calculateSubtotal() - calculateDiscount();
    return afterDiscount * (parseFloat(formData.tax_rate || 0) / 100);
  };

  const calculateTotal = () => {
    return calculateSubtotal() - calculateDiscount() + calculateTax();
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!formData.quotation_number || !formData.company_id || !formData.client_name) {
      toast.error("Please fill in all required fields");
      return;
    }

    if (quotationItems.length === 0 || !quotationItems[0].name) {
      toast.error("Please add at least one item");
      return;
    }

    const submitData = {
      ...formData,
      items: quotationItems,
      subtotal: calculateSubtotal(),
      tax_amount: calculateTax(),
      discount_amount: calculateDiscount(),
      total: calculateTotal(),
      tax_rate: parseFloat(formData.tax_rate || 0),
      discount_rate: parseFloat(formData.discount_rate || 0),
    };

    try {
      await axios.post(`${API}/quotations`, submitData);
      toast.success("Quotation created successfully");
      navigate('/quotations');
    } catch (error) {
      console.error("Error creating quotation:", error);
      toast.error("Failed to create quotation");
    }
  };

  const formatCurrency = (amount) => {
    if (formData.currency === 'IDR') {
      return new Intl.NumberFormat('id-ID', { style: 'currency', currency: 'IDR', minimumFractionDigits: 0 }).format(amount);
    }
    return new Intl.NumberFormat('en-US', { style: 'currency', currency: formData.currency }).format(amount);
  };

  return (
    <div data-testid="create-quotation-page">
      <div className="mb-6">
        <Button
          variant="ghost"
          onClick={() => navigate('/quotations')}
          data-testid="back-btn"
          className="mb-4"
        >
          <ArrowLeft size={20} className="mr-2" />
          Back to Quotations
        </Button>
        <h1 className="text-3xl font-bold text-slate-800 mb-2">Create New Quotation</h1>
        <p className="text-slate-600">Fill in the details to create a new quotation</p>
      </div>

      <form onSubmit={handleSubmit}>
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main Form */}
          <div className="lg:col-span-2 space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Quotation Information</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="quotation_number">Quotation Number *</Label>
                    <Input
                      id="quotation_number"
                      name="quotation_number"
                      data-testid="quotation-number-input"
                      value={formData.quotation_number}
                      onChange={handleInputChange}
                      placeholder="INV-001"
                      required
                    />
                  </div>
                  <div>
                    <Label htmlFor="company_id">Company *</Label>
                    <Select value={formData.company_id} onValueChange={(value) => handleSelectChange('company_id', value)}>
                      <SelectTrigger data-testid="company-select">
                        <SelectValue placeholder="Select company" />
                      </SelectTrigger>
                      <SelectContent>
                        {companies.map((company) => (
                          <SelectItem key={company.id} value={company.id}>
                            {company.name}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="date">Date *</Label>
                    <Input
                      id="date"
                      name="date"
                      type="date"
                      data-testid="quotation-date-input"
                      value={formData.date}
                      onChange={handleInputChange}
                      required
                    />
                  </div>
                  <div>
                    <Label htmlFor="valid_until">Valid Until</Label>
                    <Input
                      id="valid_until"
                      name="valid_until"
                      type="date"
                      data-testid="quotation-due-date-input"
                      value={formData.valid_until}
                      onChange={handleInputChange}
                    />
                  </div>
                </div>
                <div>
                  <Label htmlFor="currency">Currency</Label>
                  <Select value={formData.currency} onValueChange={(value) => handleSelectChange('currency', value)}>
                    <SelectTrigger data-testid="currency-select">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="IDR">IDR - Indonesian Rupiah</SelectItem>
                      <SelectItem value="USD">USD - US Dollar</SelectItem>
                      <SelectItem value="EUR">EUR - Euro</SelectItem>
                      <SelectItem value="SGD">SGD - Singapore Dollar</SelectItem>
                      <SelectItem value="MYR">MYR - Malaysian Ringgit</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <Label htmlFor="status">Status</Label>
                  <Select value={formData.status} onValueChange={(value) => handleSelectChange('status', value)}>
                    <SelectTrigger data-testid="status-select">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="draft">Draft</SelectItem>
                      <SelectItem value="sent">Sent</SelectItem>
                      <SelectItem value="paid">Paid</SelectItem>
                      <SelectItem value="overdue">Overdue</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Client Information</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <Label htmlFor="client_name">Client Name *</Label>
                  <Input
                    id="client_name"
                    name="client_name"
                    data-testid="client-name-input"
                    value={formData.client_name}
                    onChange={handleInputChange}
                    required
                  />
                </div>
                <div>
                  <Label htmlFor="client_address">Client Address</Label>
                  <Textarea
                    id="client_address"
                    name="client_address"
                    data-testid="client-address-input"
                    value={formData.client_address}
                    onChange={handleInputChange}
                    rows={2}
                  />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="client_phone">Phone</Label>
                    <Input
                      id="client_phone"
                      name="client_phone"
                      data-testid="client-phone-input"
                      value={formData.client_phone}
                      onChange={handleInputChange}
                    />
                  </div>
                  <div>
                    <Label htmlFor="client_email">Email</Label>
                    <Input
                      id="client_email"
                      name="client_email"
                      type="email"
                      data-testid="client-email-input"
                      value={formData.client_email}
                      onChange={handleInputChange}
                    />
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <div className="flex justify-between items-center">
                  <CardTitle>Items</CardTitle>
                  <Button
                    type="button"
                    variant="outline"
                    size="sm"
                    data-testid="add-item-btn"
                    onClick={addItem}
                  >
                    <Plus size={16} className="mr-2" />
                    Add Item
                  </Button>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {quotationItems.map((item, index) => (
                    <div key={index} className="border rounded-lg p-4 space-y-3">
                      <div className="flex justify-between items-start">
                        <h4 className="font-medium text-sm">Item {index + 1}</h4>
                        {quotationItems.length > 1 && (
                          <Button
                            type="button"
                            variant="ghost"
                            size="sm"
                            data-testid={`remove-item-${index}`}
                            onClick={() => removeItem(index)}
                            className="text-red-600 hover:text-red-700"
                          >
                            <Trash2 size={16} />
                          </Button>
                        )}
                      </div>
                      <div>
                        <Label>Select from Items Database (Optional)</Label>
                        <Select value={item.item_id || ""} onValueChange={(value) => handleSelectItem(index, value)}>
                          <SelectTrigger data-testid={`item-select-${index}`}>
                            <SelectValue placeholder="Select an item" />
                          </SelectTrigger>
                          <SelectContent>
                            {items.map((dbItem) => (
                              <SelectItem key={dbItem.id} value={dbItem.id}>
                                {dbItem.name} - {formatCurrency(dbItem.unit_price)}
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                      </div>
                      <div className="grid grid-cols-2 gap-3">
                        <div>
                          <Label>Item Name *</Label>
                          <Input
                            data-testid={`item-name-${index}`}
                            value={item.name}
                            onChange={(e) => handleItemChange(index, 'name', e.target.value)}
                            required
                          />
                        </div>
                        <div>
                          <Label>Description</Label>
                          <Input
                            data-testid={`item-description-${index}`}
                            value={item.description}
                            onChange={(e) => handleItemChange(index, 'description', e.target.value)}
                          />
                        </div>
                      </div>
                      <div className="grid grid-cols-4 gap-3">
                        <div>
                          <Label>Quantity *</Label>
                          <Input
                            type="number"
                            step="0.01"
                            data-testid={`item-quantity-${index}`}
                            value={item.quantity}
                            onChange={(e) => handleItemChange(index, 'quantity', e.target.value)}
                            required
                          />
                        </div>
                        <div>
                          <Label>Unit</Label>
                          <Input
                            data-testid={`item-unit-${index}`}
                            value={item.unit}
                            onChange={(e) => handleItemChange(index, 'unit', e.target.value)}
                          />
                        </div>
                        <div>
                          <Label>Unit Price *</Label>
                          <Input
                            type="number"
                            step="0.01"
                            data-testid={`item-price-${index}`}
                            value={item.unit_price}
                            onChange={(e) => handleItemChange(index, 'unit_price', e.target.value)}
                            required
                          />
                        </div>
                        <div>
                          <Label>Total</Label>
                          <Input
                            data-testid={`item-total-${index}`}
                            value={formatCurrency(item.total)}
                            disabled
                            className="bg-slate-50"
                          />
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Additional Information</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <Label htmlFor="notes">Notes</Label>
                  <Textarea
                    id="notes"
                    name="notes"
                    data-testid="notes-input"
                    value={formData.notes}
                    onChange={handleInputChange}
                    rows={3}
                    placeholder="Payment terms, additional information, etc."
                  />
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Summary Sidebar */}
          <div className="lg:col-span-1">
            <Card className="sticky top-24">
              <CardHeader>
                <CardTitle>Summary</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <Label htmlFor="discount_rate">Discount (%)</Label>
                  <Input
                    id="discount_rate"
                    name="discount_rate"
                    type="number"
                    step="0.01"
                    data-testid="discount-rate-input"
                    value={formData.discount_rate}
                    onChange={handleInputChange}
                  />
                </div>
                <div>
                  <Label htmlFor="tax_rate">Tax (%)</Label>
                  <Input
                    id="tax_rate"
                    name="tax_rate"
                    type="number"
                    step="0.01"
                    data-testid="tax-rate-input"
                    value={formData.tax_rate}
                    onChange={handleInputChange}
                  />
                </div>
                <div className="pt-4 border-t space-y-2">
                  <div className="flex justify-between text-sm">
                    <span>Subtotal:</span>
                    <span className="font-medium" data-testid="subtotal-display">{formatCurrency(calculateSubtotal())}</span>
                  </div>
                  {parseFloat(formData.discount_rate) > 0 && (
                    <div className="flex justify-between text-sm text-red-600">
                      <span>Discount ({formData.discount_rate}%):</span>
                      <span data-testid="discount-display">-{formatCurrency(calculateDiscount())}</span>
                    </div>
                  )}
                  {parseFloat(formData.tax_rate) > 0 && (
                    <div className="flex justify-between text-sm">
                      <span>Tax ({formData.tax_rate}%):</span>
                      <span data-testid="tax-display">{formatCurrency(calculateTax())}</span>
                    </div>
                  )}
                  <div className="flex justify-between text-lg font-bold pt-2 border-t">
                    <span>Total:</span>
                    <span className="text-blue-600" data-testid="total-display">{formatCurrency(calculateTotal())}</span>
                  </div>
                </div>
                <Button
                  type="submit"
                  data-testid="submit-quotation-btn"
                  className="w-full bg-blue-600 hover:bg-blue-700 mt-4"
                >
                  Create Quotation
                </Button>
              </CardContent>
            </Card>
          </div>
        </div>
      </form>
    </div>
  );
};

export default CreateQuotation;