import React, { useState, useEffect } from "react";
import { BrowserRouter, Routes, Route, Link, useLocation } from "react-router-dom";
import axios from "axios";
import { FileText, Receipt, Package, Building2, LayoutDashboard, Menu, X } from "lucide-react";
import "@/App.css";
import Dashboard from "./pages/Dashboard";
import Invoices from "./pages/Invoices";
import Quotations from "./pages/Quotations";
import Items from "./pages/Items";
import Companies from "./pages/Companies";
import CreateInvoice from "./pages/CreateInvoice";
import CreateQuotation from "./pages/CreateQuotation";
import EditInvoice from "./pages/EditInvoice";
import EditQuotation from "./pages/EditQuotation";
import { Toaster } from "@/components/ui/sonner";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
export const API = `${BACKEND_URL}/api`;

const Sidebar = ({ isOpen, setIsOpen }) => {
  const location = useLocation();
  
  const menuItems = [
    { path: "/", label: "Dashboard", icon: LayoutDashboard },
    { path: "/invoices", label: "Invoices", icon: Receipt },
    { path: "/quotations", label: "Quotations", icon: FileText },
    { path: "/items", label: "Items", icon: Package },
    { path: "/companies", label: "Companies", icon: Building2 },
  ];

  return (
    <>
      {/* Mobile Overlay */}
      {isOpen && (
        <div
          data-testid="sidebar-overlay"
          className="fixed inset-0 bg-black/50 z-40 lg:hidden"
          onClick={() => setIsOpen(false)}
        />
      )}
      
      {/* Sidebar */}
      <aside
        data-testid="sidebar"
        className={`fixed top-0 left-0 h-screen bg-white border-r border-slate-200 z-50 transition-transform duration-300 lg:translate-x-0 ${
          isOpen ? "translate-x-0" : "-translate-x-full"
        } w-64`}
      >
        <div className="flex items-center justify-between p-6 border-b border-slate-200">
          <h1 className="text-xl font-bold text-slate-800">BillMaster</h1>
          <button
            data-testid="close-sidebar-btn"
            onClick={() => setIsOpen(false)}
            className="lg:hidden text-slate-600 hover:text-slate-800"
          >
            <X size={24} />
          </button>
        </div>
        
        <nav className="p-4 space-y-2">
          {menuItems.map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname === item.path;
            return (
              <Link
                key={item.path}
                to={item.path}
                data-testid={`nav-${item.label.toLowerCase()}`}
                onClick={() => setIsOpen(false)}
                className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
                  isActive
                    ? "bg-blue-600 text-white"
                    : "text-slate-700 hover:bg-slate-100"
                }`}
              >
                <Icon size={20} />
                <span className="font-medium">{item.label}</span>
              </Link>
            );
          })}
        </nav>
      </aside>
    </>
  );
};

function AppContent() {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <div className="flex min-h-screen bg-slate-50">
      <Sidebar isOpen={sidebarOpen} setIsOpen={setSidebarOpen} />
      
      <main className="flex-1 lg:ml-64">
        {/* Top Bar */}
        <div className="bg-white border-b border-slate-200 px-6 py-4 sticky top-0 z-30">
          <div className="flex items-center gap-4">
            <button
              data-testid="open-sidebar-btn"
              onClick={() => setSidebarOpen(true)}
              className="lg:hidden text-slate-600 hover:text-slate-800"
            >
              <Menu size={24} />
            </button>
            <h2 className="text-lg font-semibold text-slate-800">Invoice & Quotation Platform</h2>
          </div>
        </div>
        
        {/* Content */}
        <div className="p-6">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/invoices" element={<Invoices />} />
            <Route path="/invoices/create" element={<CreateInvoice />} />
            <Route path="/invoices/edit/:id" element={<EditInvoice />} />
            <Route path="/quotations" element={<Quotations />} />
            <Route path="/quotations/create" element={<CreateQuotation />} />
            <Route path="/quotations/edit/:id" element={<EditQuotation />} />
            <Route path="/items" element={<Items />} />
            <Route path="/companies" element={<Companies />} />
          </Routes>
        </div>
      </main>
      
      <Toaster position="top-right" richColors />
    </div>
  );
}

function App() {
  return (
    <BrowserRouter>
      <AppContent />
    </BrowserRouter>
  );
}

export default App;