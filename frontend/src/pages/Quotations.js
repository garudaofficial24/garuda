import React, { useState, useEffect } from "react";
import axios from "axios";
import { API } from "../App";
import { Plus, Edit2, Trash2, Download, FileText, Eye } from "lucide-react";
import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from "@/components/ui/dialog";
import { toast } from "sonner";

const Quotations = () => {
  const [quotations, setQuotations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [previewQuotation, setPreviewQuotation] = useState(null);
  const [previewDialogOpen, setPreviewDialogOpen] = useState(false);

  useEffect(() => {
    fetchQuotations();
  }, []);

  const fetchQuotations = async () => {
    try {
      const response = await axios.get(`${API}/quotations`);
      setQuotations(response.data);
    } catch (error) {
      console.error("Error fetching quotations:", error);
      toast.error("Failed to fetch quotations");
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm("Are you sure you want to delete this quotation?")) {
      return;
    }

    try {
      await axios.delete(`${API}/quotations/${id}`);
      toast.success("Quotation deleted successfully");
      fetchQuotations();
    } catch (error) {
      console.error("Error deleting quotation:", error);
      toast.error("Failed to delete quotation");
    }
  };

  const handlePreview = async (quotation) => {
    try {
      const response = await axios.get(`${API}/quotations/${quotation.id}`);
      
      // Try to get company, but handle if company doesn't exist
      let companyData = null;
      try {
        const companyResponse = await axios.get(`${API}/companies/${quotation.company_id}`);
        companyData = companyResponse.data;
      } catch (companyError) {
        console.warn("Company not found, using quotation data only");
        // Create a minimal company object from quotation data if company not found
        companyData = {
          name: "Company Information Not Available",
          address: "",
          phone: "",
          email: ""
        };
      }
      
      setPreviewQuotation({ ...response.data, company: companyData });
      setPreviewDialogOpen(true);
    } catch (error) {
      console.error("Error loading preview:", error);
      toast.error("Failed to load preview. Please try again.");
    }
  };

  const handleDownloadPDF = async (id, quotationNumber) => {
    try {
      const response = await axios.get(`${API}/quotations/${id}/pdf`, {
        responseType: 'blob',
      });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `quotation_${quotationNumber}.pdf`);
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
      accepted: { variant: "success", label: "Accepted" },
      rejected: { variant: "destructive", label: "Rejected" },
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
    <div data-testid="quotations-page">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-3xl font-bold text-slate-800 mb-2">Quotations</h1>
          <p className="text-slate-600">Manage your quotations</p>
        </div>
        <Link to="/quotations/create">
          <Button data-testid="create-quotation-btn" className="bg-green-600 hover:bg-green-700">
            <Plus size={20} className="mr-2" />
            Create Quotation
          </Button>
        </Link>
      </div>

      {quotations.length === 0 ? (
        <Card>
          <CardContent className="py-12 text-center">
            <FileText className="mx-auto mb-4 text-slate-400" size={48} />
            <p className="text-slate-600 mb-4">No quotations found</p>
            <p className="text-sm text-slate-500">Create your first quotation to get started</p>
          </CardContent>
        </Card>
      ) : (
        <Card>
          <CardContent className="p-0">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Quotation Number</TableHead>
                  <TableHead>Client</TableHead>
                  <TableHead>Date</TableHead>
                  <TableHead>Total</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {quotations.map((quotation) => (
                  <TableRow key={quotation.id} data-testid={`quotation-row-${quotation.id}`}>
                    <TableCell className="font-medium">{quotation.quotation_number}</TableCell>
                    <TableCell>{quotation.client_name}</TableCell>
                    <TableCell>{quotation.date}</TableCell>
                    <TableCell className="font-semibold">{formatCurrency(quotation.total, quotation.currency)}</TableCell>
                    <TableCell>{getStatusBadge(quotation.status)}</TableCell>
                    <TableCell className="text-right">
                      <div className="flex justify-end gap-2">
                        <Button
                          size="sm"
                          variant="ghost"
                          data-testid={`preview-quotation-${quotation.id}`}
                          onClick={() => handlePreview(quotation)}
                          title="Preview"
                        >
                          <Eye size={16} />
                        </Button>
                        <Button
                          size="sm"
                          variant="ghost"
                          data-testid={`download-quotation-${quotation.id}`}
                          onClick={() => handleDownloadPDF(quotation.id, quotation.quotation_number)}
                          title="Download PDF"
                        >
                          <Download size={16} />
                        </Button>
                        <Link to={`/quotations/edit/${quotation.id}`}>
                          <Button
                            size="sm"
                            variant="ghost"
                            data-testid={`edit-quotation-${quotation.id}`}
                          >
                            <Edit2 size={16} />
                          </Button>
                        </Link>
                        <Button
                          size="sm"
                          variant="ghost"
                          data-testid={`delete-quotation-${quotation.id}`}
                          onClick={() => handleDelete(quotation.id)}
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
            <DialogTitle>Quotation Preview</DialogTitle>
            <DialogDescription>
              Preview your quotation before downloading or printing
            </DialogDescription>
          </DialogHeader>
          {previewQuotation && (
            <div className="preview-container bg-white p-8 rounded-lg border">
              {/* Header */}
              <div className="text-center mb-8">
                <h1 className="text-4xl font-bold text-green-600 mb-2">QUOTATION</h1>
              </div>

              {/* Company Info */}
              <div className="mb-6">
                <div className="flex items-start gap-4 mb-4">
                  {previewQuotation.company?.logo && (
                    <img
                      src={previewQuotation.company.logo}
                      alt="Company Logo"
                      className="w-16 h-16 object-contain border border-slate-200 rounded p-1"
                    />
                  )}
                  <div>
                    <h2 className="text-xl font-bold text-slate-800">{previewQuotation.company?.name}</h2>
                    <p className="text-sm text-slate-600">{previewQuotation.company?.address}</p>
                    <p className="text-sm text-slate-600">
                      Phone: {previewQuotation.company?.phone} | Email: {previewQuotation.company?.email}
                    </p>
                    {previewQuotation.company?.npwp && (
                      <p className="text-sm text-slate-600">NPWP: {previewQuotation.company.npwp}</p>
                    )}
                  </div>
                </div>
              </div>

              {/* Quotation Info */}
              <div className="grid grid-cols-2 gap-4 mb-6 p-4 bg-slate-50 rounded">
                <div>
                  <p className="text-sm font-semibold text-slate-700">Quotation Number:</p>
                  <p className="text-slate-800">{previewQuotation.quotation_number}</p>
                </div>
                <div>
                  <p className="text-sm font-semibold text-slate-700">Date:</p>
                  <p className="text-slate-800">{previewQuotation.date}</p>
                </div>
                <div>
                  <p className="text-sm font-semibold text-slate-700">Client:</p>
                  <p className="text-slate-800">{previewQuotation.client_name}</p>
                </div>
                <div>
                  <p className="text-sm font-semibold text-slate-700">Valid Until:</p>
                  <p className="text-slate-800">{previewQuotation.valid_until || '-'}</p>
                </div>
              </div>

              {/* Items Table */}
              <div className="mb-6">
                <table className="w-full border-collapse">
                  <thead>
                    <tr className="bg-green-600 text-white">
                      <th className="border p-2 text-left">Item</th>
                      <th className="border p-2 text-left">Description</th>
                      <th className="border p-2 text-right">Qty</th>
                      <th className="border p-2 text-right">Unit Price</th>
                      <th className="border p-2 text-right">Total</th>
                    </tr>
                  </thead>
                  <tbody>
                    {previewQuotation.items?.map((item, index) => (
                      <tr key={index} className="border">
                        <td className="border p-2">{item.name}</td>
                        <td className="border p-2 text-sm text-slate-600">{item.description}</td>
                        <td className="border p-2 text-right">{item.quantity} {item.unit}</td>
                        <td className="border p-2 text-right">{formatCurrency(item.unit_price, previewQuotation.currency)}</td>
                        <td className="border p-2 text-right font-semibold">{formatCurrency(item.total, previewQuotation.currency)}</td>
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
                    <span className="font-medium">{formatCurrency(previewQuotation.subtotal, previewQuotation.currency)}</span>
                  </div>
                  {previewQuotation.discount_amount > 0 && (
                    <div className="flex justify-between py-2 border-b text-red-600">
                      <span>Discount ({previewQuotation.discount_rate}%):</span>
                      <span>-{formatCurrency(previewQuotation.discount_amount, previewQuotation.currency)}</span>
                    </div>
                  )}
                  {previewQuotation.tax_amount > 0 && (
                    <div className="flex justify-between py-2 border-b">
                      <span className="text-slate-700">Tax ({previewQuotation.tax_rate}%):</span>
                      <span className="font-medium">{formatCurrency(previewQuotation.tax_amount, previewQuotation.currency)}</span>
                    </div>
                  )}
                  <div className="flex justify-between py-3 border-t-2 border-green-600">
                    <span className="text-lg font-bold text-slate-800">Total:</span>
                    <span className="text-lg font-bold text-green-600">{formatCurrency(previewQuotation.total, previewQuotation.currency)}</span>
                  </div>
                </div>
              </div>

              {/* Notes */}
              {previewQuotation.notes && (
                <div className="mb-6">
                  <p className="font-semibold text-slate-800 mb-2">Notes:</p>
                  <p className="text-sm text-slate-600 whitespace-pre-wrap">{previewQuotation.notes}</p>
                </div>
              )}

              {/* Bank Details */}
              {previewQuotation.company?.bank_name && (
                <div className="border-t pt-6">
                  <p className="font-semibold text-slate-800 mb-2">Payment Details:</p>
                  <p className="text-sm text-slate-600">Bank: {previewQuotation.company.bank_name}</p>
                  <p className="text-sm text-slate-600">Account: {previewQuotation.company.bank_account}</p>
                  <p className="text-sm text-slate-600">Account Name: {previewQuotation.company.bank_account_name}</p>
                </div>
              )}

              {/* Signature Section */}
              {(previewQuotation.signature_name || previewQuotation.signature_position) && (
                <div className="border-t pt-8 mt-8">
                  <div className="flex justify-end">
                    <div className="text-right">
                      <p className="font-semibold text-slate-800 mb-16">Authorized Signature:</p>
                      <div className="border-t border-slate-800 pt-2 min-w-[200px]">
                        {previewQuotation.signature_name && (
                          <p className="font-bold text-slate-800">{previewQuotation.signature_name}</p>
                        )}
                        {previewQuotation.signature_position && (
                          <p className="text-sm text-slate-600">{previewQuotation.signature_position}</p>
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
                  onClick={() => handleDownloadPDF(previewQuotation.id, previewQuotation.quotation_number)}
                  className="bg-green-600 hover:bg-green-700"
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

export default Quotations;