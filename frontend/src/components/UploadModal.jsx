import React, { useState } from 'react';
import { Upload, X, FileText, CheckCircle2, AlertCircle, Loader2 } from 'lucide-react';
import { papersApi } from '../api/client';
import { useProject } from '../contexts/ProjectContext';
import Modal from './Modal';

export default function UploadModal({ isOpen, onClose, onUploadSuccess }) {
  const { selectedProject } = useProject();
  const [files, setFiles] = useState([]);
  const [isUploading, setIsUploading] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');
  const [successCount, setSuccessCount] = useState(0);

  const handleFileChange = (e) => {
    if (e.target.files) {
      const selected = Array.from(e.target.files).filter(f => f.name.toLowerCase().endsWith('.pdf'));
      setFiles(prev => [...prev, ...selected]);
    }
  };

  const removeFile = (index) => {
    setFiles(prev => prev.filter((_, i) => i !== index));
  };

  const handleUpload = async () => {
    if (files.length === 0 || !selectedProject) return;
    setIsUploading(true);
    setErrorMsg('');
    setSuccessCount(0);

    const formData = new FormData();
    formData.append('project_id', selectedProject.id);
    files.forEach(f => formData.append('files', f));

    try {
      const res = await papersApi.upload(selectedProject.id, formData);
      const uploaded = Array.isArray(res.data) ? res.data : [];
      const indexed = uploaded.filter(p => p.status === 'indexed');
      const failed = uploaded.filter(p => p.status === 'failed');

      if (failed.length > 0) {
        const failDetails = failed
          .map(p => `${p.file_name}: ${p.error_message || 'Processing failed'}`)
          .join('; ');
        setErrorMsg(
          indexed.length > 0
            ? `Indexed ${indexed.length} paper(s), but ${failed.length} failed — ${failDetails}`
            : `Failed to process PDF(s): ${failDetails}`
        );
      }

      if (indexed.length > 0) {
        setSuccessCount(indexed.length);
        setTimeout(() => {
          setFiles([]);
          setIsUploading(false);
          if (failed.length === 0) {
            onClose();
          }
          if (onUploadSuccess) onUploadSuccess();
        }, 1200);
      } else {
        setIsUploading(false);
      }
    } catch (err) {
      console.error("Upload error:", err);
      const status = err.response?.status;
      const detail = err.response?.data?.detail;
      let message = "Failed to upload papers.";

      if (typeof detail === 'string' && detail.trim()) {
        message = detail;
      } else if (Array.isArray(detail) && detail.length > 0) {
        message = detail.map(d => d.msg || JSON.stringify(d)).join('; ');
      } else if (status === 502 || status === 504) {
        message = `Server unavailable or timed out (HTTP ${status}) while processing PDFs. Try uploading fewer or smaller files.`;
      } else if (status === 413) {
        message = "Uploaded PDF file(s) exceed the server size limit.";
      } else if (status === 401) {
        message = "Your session has expired. Please sign in again.";
      } else if (err.message) {
        message = `Upload request failed: ${err.message}`;
      }

      setErrorMsg(message);
      setIsUploading(false);
    }
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Upload Academic Research Papers (PDF)">
      <div className="space-y-4">
        {selectedProject && (
          <p className="text-xs text-slate-500">
            Target Project: <span className="font-semibold text-academic-600">{selectedProject.name}</span>
          </p>
        )}

        {/* Dropzone */}
        <label className="border-2 border-dashed border-slate-300 dark:border-slate-700 hover:border-academic-500 rounded-xl p-8 flex flex-col items-center justify-center text-center cursor-pointer bg-slate-50/50 dark:bg-navy-950/40 hover:bg-slate-50 dark:hover:bg-navy-900 transition-all">
          <Upload className="w-8 h-8 text-academic-500 mb-2" />
          <span className="text-xs font-bold text-slate-800 dark:text-slate-200">
            Click to browse or drop research papers
          </span>
          <span className="text-[11px] text-slate-400 mt-1">
            Accepts multiple PDF files (auto text extraction, chunking, and ChromaDB vector indexing)
          </span>
          <input
            type="file"
            multiple
            accept="application/pdf"
            onChange={handleFileChange}
            className="hidden"
            disabled={isUploading}
          />
        </label>

        {/* File Queue */}
        {files.length > 0 && (
          <div className="space-y-2">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-500">
              Files to Index ({files.length})
            </span>
            <div className="max-h-40 overflow-y-auto space-y-1.5 divide-y divide-slate-100 dark:divide-slate-800">
              {files.map((file, idx) => (
                <div key={idx} className="flex items-center justify-between py-1.5 text-xs">
                  <div className="flex items-center gap-2 truncate">
                    <FileText className="w-4 h-4 text-academic-500 shrink-0" />
                    <span className="truncate text-slate-800 dark:text-slate-200 font-medium">{file.name}</span>
                    <span className="text-[10px] text-slate-400">({Math.round(file.size / 1024)} KB)</span>
                  </div>
                  {!isUploading && (
                    <button
                      onClick={() => removeFile(idx)}
                      className="p-1 hover:text-rose-500 text-slate-400"
                    >
                      <X className="w-3.5 h-3.5" />
                    </button>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {errorMsg && (
          <div className="p-3 bg-rose-50 dark:bg-rose-950/40 border border-rose-200 dark:border-rose-900 rounded-lg text-xs text-rose-600 flex items-center gap-2">
            <AlertCircle className="w-4 h-4 shrink-0" />
            <span>{errorMsg}</span>
          </div>
        )}

        {successCount > 0 && (
          <div className="p-3 bg-emerald-50 dark:bg-emerald-950/40 border border-emerald-200 dark:border-emerald-900 rounded-lg text-xs text-emerald-600 flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 shrink-0" />
            <span>Successfully indexed {successCount} research papers!</span>
          </div>
        )}

        <div className="flex justify-end gap-2 pt-2">
          <button
            onClick={onClose}
            disabled={isUploading}
            className="academic-button-secondary text-xs"
          >
            Cancel
          </button>
          <button
            onClick={handleUpload}
            disabled={files.length === 0 || isUploading}
            className="academic-button-primary text-xs"
          >
            {isUploading ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                <span>Processing & Indexing Embeddings...</span>
              </>
            ) : (
              <span>Start Ingestion ({files.length} Papers)</span>
            )}
          </button>
        </div>
      </div>
    </Modal>
  );
}
