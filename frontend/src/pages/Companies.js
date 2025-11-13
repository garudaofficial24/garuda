import React, { useState, useEffect } from "react";
import axios from "axios";
import { API } from "../App";
import { Plus, Edit2, Trash2, Building2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { toast } from "sonner";

const Companies = () => {
  const [companies, setCompanies] = useState([]);
  const [loading, setLoading] = useState(true);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editingCompany, setEditingCompany] = useState(null);
  const [formData, setFormData] = useState({
    name: "",
    address: "",
    phone: "",
    email: "",
    website: "",
    npwp: "",
    bank_name: "",
    bank_account: "",
    bank_account_name: "",
    logo: "",
  });

  useEffect(() => {
    fetchCompanies();
  }, []);

  const fetchCompanies = async () => {
    try {
      const response = await axios.get(`${API}/companies`);
      setCompanies(response.data);
    } catch (error) {
      console.error("Error fetching companies:", error);
      toast.error("Failed to fetch companies");
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!formData.name.trim()) {
      toast.error("Company name is required");
      return;
    }

    try {
      if (editingCompany) {
        await axios.put(`${API}/companies/${editingCompany.id}`, formData);
        toast.success("Company updated successfully");
      } else {
        await axios.post(`${API}/companies`, formData);
        toast.success("Company created successfully");
      }
      
      setDialogOpen(false);
      setEditingCompany(null);
      resetForm();
      fetchCompanies();
    } catch (error) {
      console.error("Error saving company:", error);
      toast.error("Failed to save company");
    }
  };

  const handleEdit = (company) => {
    setEditingCompany(company);
    setFormData({
      name: company.name,
      address: company.address || "",
      phone: company.phone || "",
      email: company.email || "",
      website: company.website || "",
      npwp: company.npwp || "",
      bank_name: company.bank_name || "",
      bank_account: company.bank_account || "",
      bank_account_name: company.bank_account_name || "",
      logo: company.logo || "",
    });
    setDialogOpen(true);
  };

  const handleDelete = async (id) => {
    if (!window.confirm("Are you sure you want to delete this company?")) {
      return;
    }

    try {
      await axios.delete(`${API}/companies/${id}`);
      toast.success("Company deleted successfully");
      fetchCompanies();
    } catch (error) {
      console.error("Error deleting company:", error);
      toast.error("Failed to delete company");
    }
  };

  const resetForm = () => {
    setFormData({
      name: "",
      address: "",
      phone: "",
      email: "",
      website: "",
      npwp: "",
      bank_name: "",
      bank_account: "",
      bank_account_name: "",
      logo: "",
    });
  };

  const openCreateDialog = () => {
    setEditingCompany(null);
    resetForm();
    setDialogOpen(true);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-slate-600">Loading...</div>
      </div>
    );
  }

  return (
    <div data-testid="companies-page">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-3xl font-bold text-slate-800 mb-2">Companies</h1>
          <p className="text-slate-600">Manage your company information</p>
        </div>
        <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
          <DialogTrigger asChild>
            <Button data-testid="create-company-btn" onClick={openCreateDialog} className="bg-blue-600 hover:bg-blue-700">
              <Plus size={20} className="mr-2" />
              Add Company
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
            <DialogHeader>
              <DialogTitle>{editingCompany ? "Edit Company" : "Add New Company"}</DialogTitle>
            </DialogHeader>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <Label htmlFor="name">Company Name *</Label>
                <Input
                  id="name"
                  name="name"
                  data-testid="company-name-input"
                  value={formData.name}
                  onChange={handleInputChange}
                  required
                />
              </div>
              <div>
                <Label htmlFor="address">Address</Label>
                <Textarea
                  id="address"
                  name="address"
                  data-testid="company-address-input"
                  value={formData.address}
                  onChange={handleInputChange}
                  rows={3}
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="phone">Phone</Label>
                  <Input
                    id="phone"
                    name="phone"
                    data-testid="company-phone-input"
                    value={formData.phone}
                    onChange={handleInputChange}
                  />
                </div>
                <div>
                  <Label htmlFor="email">Email</Label>
                  <Input
                    id="email"
                    name="email"
                    type="email"
                    data-testid="company-email-input"
                    value={formData.email}
                    onChange={handleInputChange}
                  />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="website">Website</Label>
                  <Input
                    id="website"
                    name="website"
                    data-testid="company-website-input"
                    value={formData.website}
                    onChange={handleInputChange}
                  />
                </div>
                <div>
                  <Label htmlFor="npwp">NPWP</Label>
                  <Input
                    id="npwp"
                    name="npwp"
                    data-testid="company-npwp-input"
                    value={formData.npwp}
                    onChange={handleInputChange}
                  />
                </div>
              </div>
              <div>
                <Label htmlFor="bank_name">Bank Name</Label>
                <Input
                  id="bank_name"
                  name="bank_name"
                  data-testid="company-bank-name-input"
                  value={formData.bank_name}
                  onChange={handleInputChange}
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="bank_account">Bank Account Number</Label>
                  <Input
                    id="bank_account"
                    name="bank_account"
                    data-testid="company-bank-account-input"
                    value={formData.bank_account}
                    onChange={handleInputChange}
                  />
                </div>
                <div>
                  <Label htmlFor="bank_account_name">Account Name</Label>
                  <Input
                    id="bank_account_name"
                    name="bank_account_name"
                    data-testid="company-bank-account-name-input"
                    value={formData.bank_account_name}
                    onChange={handleInputChange}
                  />
                </div>
              </div>
              <div className="flex justify-end gap-2 pt-4">
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => setDialogOpen(false)}
                  data-testid="cancel-company-btn"
                >
                  Cancel
                </Button>
                <Button type="submit" data-testid="save-company-btn" className="bg-blue-600 hover:bg-blue-700">
                  {editingCompany ? "Update" : "Create"}
                </Button>
              </div>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      {companies.length === 0 ? (
        <Card>
          <CardContent className="py-12 text-center">
            <Building2 className="mx-auto mb-4 text-slate-400" size={48} />
            <p className="text-slate-600 mb-4">No companies found</p>
            <p className="text-sm text-slate-500">Create your first company to get started</p>
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {companies.map((company) => (
            <Card key={company.id} data-testid={`company-card-${company.id}`} className="card-hover">
              <CardHeader className="pb-3">
                <div className="flex justify-between items-start">
                  <div>
                    <CardTitle className="text-lg">{company.name}</CardTitle>
                  </div>
                  <div className="flex gap-2">
                    <Button
                      size="sm"
                      variant="ghost"
                      data-testid={`edit-company-${company.id}`}
                      onClick={() => handleEdit(company)}
                    >
                      <Edit2 size={16} />
                    </Button>
                    <Button
                      size="sm"
                      variant="ghost"
                      data-testid={`delete-company-${company.id}`}
                      onClick={() => handleDelete(company.id)}
                      className="text-red-600 hover:text-red-700 hover:bg-red-50"
                    >
                      <Trash2 size={16} />
                    </Button>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-2 text-sm">
                  {company.address && (
                    <p className="text-slate-600">{company.address}</p>
                  )}
                  {company.phone && (
                    <p className="text-slate-600">Phone: {company.phone}</p>
                  )}
                  {company.email && (
                    <p className="text-slate-600">Email: {company.email}</p>
                  )}
                  {company.npwp && (
                    <p className="text-slate-600">NPWP: {company.npwp}</p>
                  )}
                  {company.bank_name && (
                    <p className="text-slate-600">Bank: {company.bank_name}</p>
                  )}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
};

export default Companies;