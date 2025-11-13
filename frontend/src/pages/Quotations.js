import React, { useState, useEffect } from "react";
import axios from "axios";
import { API } from "../App";
import { Plus, Edit2, Trash2, Download, FileText, Eye } from "lucide-react";
import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
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
      const companyResponse = await axios.get(`${API}/companies/${quotation.company_id}`);
      setPreviewQuotation({ ...response.data, company: companyResponse.data });
      setPreviewDialogOpen(true);
    } catch (error) {
      console.error("Error loading preview:", error);
      toast.error("Failed to load preview");
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
    </div>
  );
};

export default Quotations;