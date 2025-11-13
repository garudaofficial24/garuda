import React, { useState, useEffect } from "react";
import axios from "axios";
import { API } from "../App";
import { Plus, Edit2, Trash2, Download, Receipt, Eye, X } from "lucide-react";
import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from "@/components/ui/dialog";
import { toast } from "sonner";

const Invoices = () => {
  const [invoices, setInvoices] = useState([]);
  const [loading, setLoading] = useState(true);
  const [previewInvoice, setPreviewInvoice] = useState(null);
  const [previewDialogOpen, setPreviewDialogOpen] = useState(false);

  useEffect(() => {
    fetchInvoices();
  }, []);

  const fetchInvoices = async () => {
    try {
      const response = await axios.get(`${API}/invoices`);
      setInvoices(response.data);
    } catch (error) {
      console.error("Error fetching invoices:", error);
      toast.error("Failed to fetch invoices");
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm("Are you sure you want to delete this invoice?")) {
      return;
    }

    try {
      await axios.delete(`${API}/invoices/${id}`);
      toast.success("Invoice deleted successfully");
      fetchInvoices();
    } catch (error) {
      console.error("Error deleting invoice:", error);
      toast.error("Failed to delete invoice");
    }
  };

  const handlePreview = async (invoice) => {
    try {
      const response = await axios.get(`${API}/invoices/${invoice.id}`);
      
      // Try to get company, but handle if company doesn't exist
      let companyData = null;
      try {
        const companyResponse = await axios.get(`${API}/companies/${invoice.company_id}`);
        companyData = companyResponse.data;
      } catch (companyError) {
        console.warn("Company not found, using invoice data only");
        // Create a minimal company object from invoice data if company not found
        companyData = {
          name: "Company Information Not Available",
          address: "",
          phone: "",
          email: ""
        };
      }
      
      setPreviewInvoice({ ...response.data, company: companyData });
      setPreviewDialogOpen(true);
    } catch (error) {
      console.error("Error loading preview:", error);
      toast.error("Failed to load preview. Please try again.");
    }
  };

  const handleDownloadPDF = async (id, invoiceNumber) => {
    try {
      const response = await axios.get(`${API}/invoices/${id}/pdf`, {
        responseType: 'blob',
      });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `invoice_${invoiceNumber}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      toast.success("PDF downloaded successfully");
    } catch (error) {
      console.error("Error downloading PDF:", error);
      toast.error("Failed to download PDF");
    }
  };

  const formatCurrency = (amount, currency) => {
    if (currency === 'IDR') {
      return new Intl.NumberFormat('id-ID', { style: 'currency', currency: 'IDR', minimumFractionDigits: 0 }).format(amount);
    } else if (currency === 'USD') {
      return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(amount);
    } else if (currency === 'EUR') {
      return new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(amount);
    }
    return `${currency} ${amount}`;
  };

  const getStatusBadge = (status) => {
    const statusConfig = {
      draft: { variant: "secondary", label: "Draft" },
      sent: { variant: "default", label: "Sent" },
      paid: { variant: "success", label: "Paid" },
      overdue: { variant: "destructive", label: "Overdue" },
    };
    const config = statusConfig[status] || statusConfig.draft;
    return <Badge variant={config.variant}>{config.label}</Badge>;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-slate-600">Loading...</div>
      </div>
    );
  }

  return (
    <div data-testid="invoices-page">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-3xl font-bold text-slate-800 mb-2">Invoices</h1>
          <p className="text-slate-600">Manage your invoices</p>
        </div>
        <Link to="/invoices/create">
          <Button data-testid="create-invoice-btn" className="bg-blue-600 hover:bg-blue-700">
            <Plus size={20} className="mr-2" />
            Create Invoice
          </Button>
        </Link>
      </div>

      {invoices.length === 0 ? (
        <Card>
          <CardContent className="py-12 text-center">
            <Receipt className="mx-auto mb-4 text-slate-400" size={48} />
            <p className="text-slate-600 mb-4">No invoices found</p>
            <p className="text-sm text-slate-500">Create your first invoice to get started</p>
          </CardContent>
        </Card>
      ) : (
        <Card>
          <CardContent className="p-0">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Invoice Number</TableHead>
                  <TableHead>Client</TableHead>
                  <TableHead>Date</TableHead>
                  <TableHead>Total</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {invoices.map((invoice) => (
                  <TableRow key={invoice.id} data-testid={`invoice-row-${invoice.id}`}>
                    <TableCell className="font-medium">{invoice.invoice_number}</TableCell>
                    <TableCell>{invoice.client_name}</TableCell>
                    <TableCell>{invoice.date}</TableCell>
                    <TableCell className="font-semibold">{formatCurrency(invoice.total, invoice.currency)}</TableCell>
                    <TableCell>{getStatusBadge(invoice.status)}</TableCell>
                    <TableCell className="text-right">
                      <div className="flex justify-end gap-2">
                        <Button
                          size="sm"
                          variant="ghost"
                          data-testid={`preview-invoice-${invoice.id}`}
                          onClick={() => handlePreview(invoice)}
                          title="Preview"
                        >
                          <Eye size={16} />
                        </Button>
                        <Button
                          size="sm"
                          variant="ghost"
                          data-testid={`download-invoice-${invoice.id}`}
                          onClick={() => handleDownloadPDF(invoice.id, invoice.invoice_number)}
                          title="Download PDF"
                        >
                          <Download size={16} />
                        </Button>
                        <Link to={`/invoices/edit/${invoice.id}`}>
                          <Button
                            size="sm"
                            variant="ghost"
                            data-testid={`edit-invoice-${invoice.id}`}
                          >
                            <Edit2 size={16} />
                          </Button>
                        </Link>
                        <Button
                          size="sm"
                          variant="ghost"
                          data-testid={`delete-invoice-${invoice.id}`}
                          onClick={() => handleDelete(invoice.id)}
                          className="text-red-600 hover:text-red-700 hover:bg-red-50"
                        >
                          <Trash2 size={16} />
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      )}

      {/* Preview Dialog */}
      <Dialog open={previewDialogOpen} onOpenChange={setPreviewDialogOpen}>
        <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Invoice Preview</DialogTitle>
            <DialogDescription>
              Preview your invoice before downloading or printing
            </DialogDescription>
          </DialogHeader>
          {previewInvoice && (
            <div className="preview-container bg-white p-8 rounded-lg border">
              {/* Header */}
              <div className="text-center mb-8">
                <h1 className="text-4xl font-bold text-blue-600 mb-2">INVOICE</h1>
              </div>

              {/* Company Info */}
              <div className="mb-6">
                <div className="flex items-start gap-4 mb-4">
                  {previewInvoice.company?.logo && (
                    <img
                      src={previewInvoice.company.logo}
                      alt="Company Logo"
                      className="w-16 h-16 object-contain border border-slate-200 rounded p-1"
                    />
                  )}
                  <div>
                    <h2 className="text-xl font-bold text-slate-800">{previewInvoice.company?.name}</h2>
                    <p className="text-sm text-slate-600">{previewInvoice.company?.address}</p>
                    <p className="text-sm text-slate-600">
                      Phone: {previewInvoice.company?.phone} | Email: {previewInvoice.company?.email}
                    </p>
                    {previewInvoice.company?.npwp && (
                      <p className="text-sm text-slate-600">NPWP: {previewInvoice.company.npwp}</p>
                    )}
                  </div>
                </div>
              </div>

              {/* Invoice Info */}
              <div className="grid grid-cols-2 gap-4 mb-6 p-4 bg-slate-50 rounded">
                <div>
                  <p className="text-sm font-semibold text-slate-700">Invoice Number:</p>
                  <p className="text-slate-800">{previewInvoice.invoice_number}</p>
                </div>
                <div>
                  <p className="text-sm font-semibold text-slate-700">Date:</p>
                  <p className="text-slate-800">{previewInvoice.date}</p>
                </div>
                <div>
                  <p className="text-sm font-semibold text-slate-700">Client:</p>
                  <p className="text-slate-800">{previewInvoice.client_name}</p>
                </div>
                <div>
                  <p className="text-sm font-semibold text-slate-700">Due Date:</p>
                  <p className="text-slate-800">{previewInvoice.due_date || '-'}</p>
                </div>
              </div>

              {/* Items Table */}
              <div className="mb-6">
                <table className="w-full border-collapse">
                  <thead>
                    <tr className="bg-blue-600 text-white">
                      <th className="border p-2 text-left">Item</th>
                      <th className="border p-2 text-left">Description</th>
                      <th className="border p-2 text-right">Qty</th>
                      <th className="border p-2 text-right">Unit Price</th>
                      <th className="border p-2 text-right">Total</th>
                    </tr>
                  </thead>
                  <tbody>
                    {previewInvoice.items?.map((item, index) => (
                      <tr key={index} className="border">
                        <td className="border p-2">{item.name}</td>
                        <td className="border p-2 text-sm text-slate-600">{item.description}</td>
                        <td className="border p-2 text-right">{item.quantity} {item.unit}</td>
                        <td className="border p-2 text-right">{formatCurrency(item.unit_price, previewInvoice.currency)}</td>
                        <td className="border p-2 text-right font-semibold">{formatCurrency(item.total, previewInvoice.currency)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {/* Summary */}
              <div className="flex justify-end mb-6">
                <div className="w-80">
                  <div className="flex justify-between py-2 border-b">
                    <span className="text-slate-700">Subtotal:</span>
                    <span className="font-medium">{formatCurrency(previewInvoice.subtotal, previewInvoice.currency)}</span>
                  </div>
                  {previewInvoice.discount_amount > 0 && (
                    <div className="flex justify-between py-2 border-b text-red-600">
                      <span>Discount ({previewInvoice.discount_rate}%):</span>
                      <span>-{formatCurrency(previewInvoice.discount_amount, previewInvoice.currency)}</span>
                    </div>
                  )}
                  {previewInvoice.tax_amount > 0 && (
                    <div className="flex justify-between py-2 border-b">
                      <span className="text-slate-700">Tax ({previewInvoice.tax_rate}%):</span>
                      <span className="font-medium">{formatCurrency(previewInvoice.tax_amount, previewInvoice.currency)}</span>
                    </div>
                  )}
                  <div className="flex justify-between py-3 border-t-2 border-blue-600">
                    <span className="text-lg font-bold text-slate-800">Total:</span>
                    <span className="text-lg font-bold text-blue-600">{formatCurrency(previewInvoice.total, previewInvoice.currency)}</span>
                  </div>
                </div>
              </div>

              {/* Notes */}
              {previewInvoice.notes && (
                <div className="mb-6">
                  <p className="font-semibold text-slate-800 mb-2">Notes:</p>
                  <p className="text-sm text-slate-600 whitespace-pre-wrap">{previewInvoice.notes}</p>
                </div>
              )}

              {/* Bank Details */}
              {previewInvoice.company?.bank_name && (
                <div className="border-t pt-6">
                  <p className="font-semibold text-slate-800 mb-2">Payment Details:</p>
                  <p className="text-sm text-slate-600">Bank: {previewInvoice.company.bank_name}</p>
                  <p className="text-sm text-slate-600">Account: {previewInvoice.company.bank_account}</p>
                  <p className="text-sm text-slate-600">Account Name: {previewInvoice.company.bank_account_name}</p>
                </div>
              )}

              {/* Signature Section */}
              {(previewInvoice.signature_name || previewInvoice.signature_position) && (
                <div className="border-t pt-8 mt-8">
                  <div className="flex justify-end">
                    <div className="text-right">
                      <p className="font-semibold text-slate-800 mb-16">Authorized Signature:</p>
                      <div className="border-t border-slate-800 pt-2 min-w-[200px]">
                        {previewInvoice.signature_name && (
                          <p className="font-bold text-slate-800">{previewInvoice.signature_name}</p>
                        )}
                        {previewInvoice.signature_position && (
                          <p className="text-sm text-slate-600">{previewInvoice.signature_position}</p>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* Action Buttons */}
              <div className="flex justify-end gap-3 mt-6 pt-6 border-t">
                <Button
                  variant="outline"
                  onClick={() => setPreviewDialogOpen(false)}
                  data-testid="close-preview-btn"
                >
                  Close
                </Button>
                <Button
                  onClick={() => handleDownloadPDF(previewInvoice.id, previewInvoice.invoice_number)}
                  className="bg-blue-600 hover:bg-blue-700"
                  data-testid="download-from-preview-btn"
                >
                  <Download size={16} className="mr-2" />
                  Download PDF
                </Button>
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default Invoices;