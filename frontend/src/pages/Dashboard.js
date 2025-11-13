import React, { useState, useEffect } from "react";
import axios from "axios";
import { API } from "../App";
import { Receipt, FileText, Package, Building2, TrendingUp } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

const Dashboard = () => {
  const [stats, setStats] = useState({
    invoices: 0,
    quotations: 0,
    items: 0,
    companies: 0,
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      const [invoicesRes, quotationsRes, itemsRes, companiesRes] = await Promise.all([
        axios.get(`${API}/invoices`),
        axios.get(`${API}/quotations`),
        axios.get(`${API}/items`),
        axios.get(`${API}/companies`),
      ]);

      setStats({
        invoices: invoicesRes.data.length,
        quotations: quotationsRes.data.length,
        items: itemsRes.data.length,
        companies: companiesRes.data.length,
      });
    } catch (error) {
      console.error("Error fetching stats:", error);
    } finally {
      setLoading(false);
    }
  };

  const statCards = [
    {
      title: "Total Invoices",
      value: stats.invoices,
      icon: Receipt,
      color: "bg-blue-500",
      testId: "stat-invoices"
    },
    {
      title: "Total Quotations",
      value: stats.quotations,
      icon: FileText,
      color: "bg-green-500",
      testId: "stat-quotations"
    },
    {
      title: "Total Items",
      value: stats.items,
      icon: Package,
      color: "bg-purple-500",
      testId: "stat-items"
    },
    {
      title: "Total Companies",
      value: stats.companies,
      icon: Building2,
      color: "bg-orange-500",
      testId: "stat-companies"
    },
  ];

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-slate-600">Loading...</div>
      </div>
    );
  }

  return (
    <div data-testid="dashboard-page">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-slate-800 mb-2">Dashboard</h1>
        <p className="text-slate-600">Welcome to your invoice and quotation management system</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {statCards.map((stat) => {
          const Icon = stat.icon;
          return (
            <Card key={stat.title} data-testid={stat.testId} className="card-hover">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-slate-600 mb-1">{stat.title}</p>
                    <p className="text-3xl font-bold text-slate-800">{stat.value}</p>
                  </div>
                  <div className={`${stat.color} p-3 rounded-lg text-white`}>
                    <Icon size={24} />
                  </div>
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>

      <div className="mt-8 grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Quick Actions</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <a
                href="/invoices/create"
                data-testid="quick-action-create-invoice"
                className="flex items-center gap-3 p-4 rounded-lg bg-blue-50 hover:bg-blue-100 text-blue-700 transition-colors"
              >
                <Receipt size={20} />
                <span className="font-medium">Create New Invoice</span>
              </a>
              <a
                href="/quotations/create"
                data-testid="quick-action-create-quotation"
                className="flex items-center gap-3 p-4 rounded-lg bg-green-50 hover:bg-green-100 text-green-700 transition-colors"
              >
                <FileText size={20} />
                <span className="font-medium">Create New Quotation</span>
              </a>
              <a
                href="/items"
                data-testid="quick-action-manage-items"
                className="flex items-center gap-3 p-4 rounded-lg bg-purple-50 hover:bg-purple-100 text-purple-700 transition-colors"
              >
                <Package size={20} />
                <span className="font-medium">Manage Items</span>
              </a>
              <a
                href="/companies"
                data-testid="quick-action-manage-companies"
                className="flex items-center gap-3 p-4 rounded-lg bg-orange-50 hover:bg-orange-100 text-orange-700 transition-colors"
              >
                <Building2 size={20} />
                <span className="font-medium">Manage Companies</span>
              </a>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Getting Started</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex gap-3">
                <div className="flex-shrink-0 w-8 h-8 bg-blue-100 text-blue-700 rounded-full flex items-center justify-center font-bold">1</div>
                <div>
                  <h4 className="font-semibold text-slate-800">Add Your Company</h4>
                  <p className="text-sm text-slate-600">Set up your company information and logo</p>
                </div>
              </div>
              <div className="flex gap-3">
                <div className="flex-shrink-0 w-8 h-8 bg-blue-100 text-blue-700 rounded-full flex items-center justify-center font-bold">2</div>
                <div>
                  <h4 className="font-semibold text-slate-800">Create Items Database</h4>
                  <p className="text-sm text-slate-600">Add your products or services for quick selection</p>
                </div>
              </div>
              <div className="flex gap-3">
                <div className="flex-shrink-0 w-8 h-8 bg-blue-100 text-blue-700 rounded-full flex items-center justify-center font-bold">3</div>
                <div>
                  <h4 className="font-semibold text-slate-800">Generate Documents</h4>
                  <p className="text-sm text-slate-600">Create invoices and quotations in seconds</p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default Dashboard;