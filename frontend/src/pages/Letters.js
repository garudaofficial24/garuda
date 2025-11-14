import React, { useState, useEffect } from "react";
import axios from "axios";
import { API } from "../App";
import { useNavigate } from "react-router-dom";
import { Plus, Edit2, Trash2, Download, Eye, Mail } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { toast } from "sonner";

const Letters = () => {
  const navigate = useNavigate();
  const [letters, setLetters] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchLetters();
  }, []);

  const fetchLetters = async () => {
    try {
      const response = await axios.get(`${API}/letters`);
      setLetters(response.data);
    } catch (error) {
      console.error("Error fetching letters:", error);
      toast.error("Failed to fetch letters");
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm("Are you sure you want to delete this letter?")) return;

    try {
      await axios.delete(`${API}/letters/${id}`);
      toast.success("Letter deleted successfully");
      fetchLetters();
    } catch (error) {
      console.error("Error deleting letter:", error);
      toast.error("Failed to delete letter");
    }
  };

  const handleDownload = async (id, letterNumber) => {
    try {
      const response = await axios.get(`${API}/letters/${id}/pdf`, {
        responseType: 'blob'
      });
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `letter_${letterNumber.replace('/', '_')}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      
      toast.success("Letter downloaded successfully");
    } catch (error) {
      console.error("Error downloading letter:", error);
      toast.error("Failed to download letter");
    }
  };

  const handlePreview = async (id) => {
    try {
      // Open PDF in new tab for better compatibility
      const pdfUrl = `${API}/letters/${id}/pdf`;
      window.open(pdfUrl, '_blank');
      toast.success("PDF dibuka di tab baru");
    } catch (error) {
      console.error("Error previewing letter:", error);
      toast.error("Failed to preview letter");
    }
  };

  const getLetterTypeLabel = (type) => {
    const types = {
      general: "Surat Umum",
      cooperation: "Surat Penawaran Kerja Sama",
      request: "Surat Permohonan"
    };
    return types[type] || type;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-slate-600">Loading...</div>
      </div>
    );
  }

  return (
    <div data-testid="letters-page">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-3xl font-bold text-slate-800 mb-2">Surat Menyurat</h1>
          <p className="text-slate-600">Kelola surat resmi perusahaan</p>
        </div>
        <Button
          onClick={() => navigate('/letters/create')}
          data-testid="create-letter-btn"
          className="bg-blue-600 hover:bg-blue-700"
        >
          <Plus size={20} className="mr-2" />
          Buat Surat Baru
        </Button>
      </div>

      {letters.length === 0 ? (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-16">
            <Mail size={64} className="text-slate-300 mb-4" />
            <h3 className="text-xl font-semibold text-slate-600 mb-2">Belum Ada Surat</h3>
            <p className="text-slate-500 mb-6">Mulai dengan membuat surat pertama Anda</p>
            <Button
              onClick={() => navigate('/letters/create')}
              className="bg-blue-600 hover:bg-blue-700"
            >
              <Plus size={20} className="mr-2" />
              Buat Surat Baru
            </Button>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-6">
          {letters.map((letter) => (
            <Card key={letter.id} className="hover:shadow-lg transition-shadow">
              <CardHeader className="border-b">
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <CardTitle className="text-xl mb-2">{letter.subject}</CardTitle>
                    <div className="flex flex-wrap gap-4 text-sm text-slate-600">
                      <span>No: <strong>{letter.letter_number}</strong></span>
                      <span>Tanggal: {letter.date}</span>
                      <span className="px-2 py-1 bg-blue-100 text-blue-800 rounded">
                        {getLetterTypeLabel(letter.letter_type)}
                      </span>
                    </div>
                  </div>
                  <div className="flex gap-2">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handlePreview(letter.id)}
                      data-testid={`preview-letter-${letter.id}`}
                      className="text-blue-600 hover:text-blue-700"
                    >
                      <Eye size={18} />
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleDownload(letter.id, letter.letter_number)}
                      data-testid={`download-letter-${letter.id}`}
                      className="text-green-600 hover:text-green-700"
                    >
                      <Download size={18} />
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => navigate(`/letters/edit/${letter.id}`)}
                      data-testid={`edit-letter-${letter.id}`}
                      className="text-slate-600 hover:text-slate-700"
                    >
                      <Edit2 size={18} />
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleDelete(letter.id)}
                      data-testid={`delete-letter-${letter.id}`}
                      className="text-red-600 hover:text-red-700"
                    >
                      <Trash2 size={18} />
                    </Button>
                  </div>
                </div>
              </CardHeader>
              <CardContent className="pt-4">
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="text-slate-500">Penerima:</span>
                    <p className="font-medium">{letter.recipient_name}</p>
                    {letter.recipient_position && (
                      <p className="text-slate-600">{letter.recipient_position}</p>
                    )}
                  </div>
                  <div>
                    <span className="text-slate-500">Penandatangan:</span>
                    {letter.signatories && letter.signatories.length > 0 ? (
                      <div>
                        {letter.signatories.map((sig, idx) => (
                          <p key={idx} className="font-medium">
                            {sig.name} - {sig.position}
                          </p>
                        ))}
                      </div>
                    ) : (
                      <p className="text-slate-400">-</p>
                    )}
                  </div>
                </div>
                {letter.content && (
                  <div className="mt-4">
                    <p className="text-slate-700 line-clamp-2">{letter.content}</p>
                  </div>
                )}
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Preview Dialog */}
      <Dialog open={previewOpen} onOpenChange={setPreviewOpen}>
        <DialogContent className="max-w-4xl h-[80vh]">
          <DialogHeader>
            <DialogTitle>Preview Surat</DialogTitle>
          </DialogHeader>
          {previewUrl && (
            <div className="w-full h-full flex flex-col">
              <object
                data={previewUrl}
                type="application/pdf"
                className="w-full flex-1"
              >
                <div className="flex flex-col items-center justify-center h-full space-y-4">
                  <p className="text-slate-600">Browser Anda tidak support preview PDF</p>
                  <Button
                    onClick={() => window.open(previewUrl, '_blank')}
                    className="bg-blue-600 hover:bg-blue-700"
                  >
                    Buka di Tab Baru
                  </Button>
                </div>
              </object>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default Letters;