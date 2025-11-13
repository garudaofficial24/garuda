import React, { useState, useEffect } from "react";
import axios from "axios";
import { API } from "../App";
import { Plus, Edit2, Trash2, Download, Receipt, Eye } from "lucide-react";
import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { toast } from "sonner";

const Invoices = () => {
  const [invoices, setInvoices] = useState([]);
  const [loading, setLoading] = useState(true);

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
    </div>
  );
};

export default Invoices;