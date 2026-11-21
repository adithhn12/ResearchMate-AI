import React, { useState, useEffect } from 'react';
import { 
  BookOpen, 
  Search, 
  Filter, 
  Trash2, 
  FileText, 
  Calendar, 
  User, 
  CheckCircle2, 
  AlertCircle, 
  Loader2, 
  Upload, 
  Layers, 
  Tag, 
  ChevronRight,
  ExternalLink
} from 'lucide-react';
import { papersApi } from '../api/client';
import { useProject } from '../contexts/ProjectContext';
import Modal from '../components/Modal';

export default function Library({ onOpenUpload }) {
  const { selectedProject } = useProject();
  const [papers, setPapers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedYear, setSelectedYear] = useState('');
  const [selectedStatus, setSelectedStatus] = useState('');
  const [viewPaper, setViewPaper] = useState(null);
  const [deletingId, setDeletingId] = useState(null);

  const fetchPapers = async () => {
    if (!selectedProject) return;
    setLoading(true);
    try {
      const params = {};
      if (searchQuery) params.query = searchQuery;
      if (selectedYear) params.year = parseInt(selectedYear);
      if (selectedStatus) params.status = selectedStatus;

      const res = await papersApi.listByProject(selectedProject.id, params);
      setPapers(res.data);
    } catch (err) {
      console.error("Error fetching papers:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPapers();
  }, [selectedProject, searchQuery, selectedYear, selectedStatus]);

  const handleDeletePaper = async (paperId) => {
    if (!window.confirm("Are you sure you want to delete this research paper and its vector embeddings?")) return;
    setDeletingId(paperId);
    try {
      await papersApi.delete(paperId);
      setPapers(prev => prev.filter(p => p.id !== paperId));
      if (viewPaper?.id === paperId) setViewPaper(null);
    } catch (err) {
      console.error("Error deleting paper:", err);
    } finally {
      setDeletingId(null);
    }
  };

  const handleOpenDetail = async (paper) => {
    try {
      const res = await papersApi.get(paper.id);
      setViewPaper(res.data);
    } catch (err) {
      setViewPaper(paper);
    }
  };

  // Distinct publication years for filter
  const years = Array.from(new Set(papers.map(p => p.publication_year).filter(Boolean))).sort((a, b) => b - a);

  return (
    <div className="p-4 sm:p-6 lg:p-8 space-y-6 max-w-7xl mx-auto min-w-0">
      {/* Header with Title & Action */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-slate-900 dark:text-white">
            Research Paper Library
          </h2>
          <p className="text-xs text-slate-500 dark:text-slate-400">
            Manage, inspect, and organize your indexed academic literature
          </p>
        </div>
        <button
          onClick={onOpenUpload}
          className="academic-button-primary text-xs"
        >
          <Upload className="w-4 h-4" />
          <span>Upload Academic Papers</span>
        </button>
      </div>

      {/* Filter and Search Bar */}
      <div className="academic-card p-4 flex flex-col md:flex-row items-stretch md:items-center justify-between gap-3">
        <div className="relative flex-1">
          <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
          <input
            type="text"
            placeholder="Search papers by title, author, abstract, or keywords..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-9 pr-4 py-2 bg-slate-50 dark:bg-navy-950 border border-slate-200 dark:border-slate-800 rounded-lg text-xs text-slate-900 dark:text-white placeholder-slate-400 focus:outline-none focus:ring-1 focus:ring-academic-500"
          />
        </div>

        <div className="flex items-center gap-2">
          <select
            value={selectedYear}
            onChange={(e) => setSelectedYear(e.target.value)}
            className="bg-slate-50 dark:bg-navy-950 border border-slate-200 dark:border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-700 dark:text-slate-300 focus:outline-none"
          >
            <option value="">All Publication Years</option>
            {years.map(yr => (
              <option key={yr} value={yr}>{yr}</option>
            ))}
          </select>

          <select
            value={selectedStatus}
            onChange={(e) => setSelectedStatus(e.target.value)}
            className="bg-slate-50 dark:bg-navy-950 border border-slate-200 dark:border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-700 dark:text-slate-300 focus:outline-none"
          >
            <option value="">All Statuses</option>
            <option value="indexed">Indexed</option>
            <option value="processing">Processing</option>
            <option value="failed">Failed</option>
          </select>
        </div>
      </div>

      {/* Papers Grid */}
      {loading ? (
        <div className="flex flex-col items-center justify-center h-64 gap-2">
          <Loader2 className="w-6 h-6 text-academic-600 animate-spin" />
          <p className="text-xs text-slate-400">Loading library papers...</p>
        </div>
      ) : papers.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {papers.map((paper) => (
            <div 
              key={paper.id} 
              className="academic-card p-5 flex flex-col justify-between hover:border-academic-400 dark:hover:border-academic-700 transition-all group"
            >
              <div className="space-y-3">
                {/* Status & Year Badges */}
                <div className="flex items-center justify-between gap-2">
                  <span className={`inline-flex items-center gap-1 text-[10px] font-semibold px-2 py-0.5 rounded-full ${
                    paper.status === 'indexed'
                      ? 'bg-emerald-50 text-emerald-700 dark:bg-emerald-950/60 dark:text-emerald-400 border border-emerald-200 dark:border-emerald-800'
                      : paper.status === 'processing'
                      ? 'bg-blue-50 text-blue-700 dark:bg-blue-950/60 dark:text-blue-400 border border-blue-200 dark:border-blue-800'
                      : 'bg-rose-50 text-rose-700 dark:bg-rose-950/60 dark:text-rose-400 border border-rose-200 dark:border-rose-800'
                  }`}>
                    {paper.status === 'indexed' && <CheckCircle2 className="w-3 h-3" />}
                    {paper.status === 'processing' && <Loader2 className="w-3 h-3 animate-spin" />}
                    {paper.status === 'failed' && <AlertCircle className="w-3 h-3" />}
                    {paper.status}
                  </span>

                  <div className="flex items-center gap-1.5 text-xs text-slate-400">
                    <Calendar className="w-3 h-3" />
                    <span>{paper.publication_year || 'Year N/A'}</span>
                  </div>
                </div>

                {/* Title */}
                <h3 
                  onClick={() => handleOpenDetail(paper)}
                  className="font-bold text-sm text-slate-900 dark:text-white line-clamp-2 cursor-pointer group-hover:text-academic-600 dark:group-hover:text-academic-400 transition-colors"
                >
                  {paper.title}
                </h3>

                {/* Authors */}
                <p className="text-xs text-slate-500 dark:text-slate-400 flex items-center gap-1.5 line-clamp-1">
                  <User className="w-3.5 h-3.5 shrink-0 text-slate-400" />
                  <span>{paper.authors || 'Unknown Authors'}</span>
                </p>

                {/* Abstract Preview */}
                <p className="text-xs text-slate-600 dark:text-slate-300 line-clamp-3 leading-relaxed">
                  {paper.abstract || 'No abstract extracted.'}
                </p>

                {/* Keywords Chips */}
                {paper.keywords && (
                  <div className="flex flex-wrap gap-1 pt-1">
                    {paper.keywords.split(',').slice(0, 3).map((kw, i) => (
                      <span 
                        key={i}
                        className="text-[10px] px-2 py-0.5 rounded bg-slate-100 text-slate-600 dark:bg-navy-800 dark:text-slate-300 font-medium"
                      >
                        {kw.trim()}
                      </span>
                    ))}
                  </div>
                )}
              </div>

              {/* Bottom Meta & Actions */}
              <div className="pt-4 mt-4 border-t border-slate-100 dark:border-slate-800 flex items-center justify-between text-xs text-slate-400">
                <span>{paper.page_count} pages • {paper.file_size ? `${Math.round(paper.file_size / 1024)} KB` : 'PDF'}</span>
                
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => handleOpenDetail(paper)}
                    className="p-1.5 text-academic-600 dark:text-academic-400 hover:bg-academic-50 dark:hover:bg-navy-800 rounded-lg transition-colors"
                    title="View Full Metadata"
                  >
                    <ExternalLink className="w-3.5 h-3.5" />
                  </button>
                  <button
                    onClick={() => handleDeletePaper(paper.id)}
                    disabled={deletingId === paper.id}
                    className="p-1.5 text-rose-500 hover:bg-rose-50 dark:hover:bg-rose-950/40 rounded-lg transition-colors"
                    title="Delete Paper"
                  >
                    {deletingId === paper.id ? (
                      <Loader2 className="w-3.5 h-3.5 animate-spin" />
                    ) : (
                      <Trash2 className="w-3.5 h-3.5" />
                    )}
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="academic-card p-12 text-center space-y-4">
          <BookOpen className="w-12 h-12 text-slate-300 dark:text-slate-700 mx-auto" />
          <div className="space-y-1">
            <h3 className="font-bold text-base text-slate-900 dark:text-white">
              No Papers Found in This Project
            </h3>
            <p className="text-xs text-slate-500 max-w-sm mx-auto">
              Upload multiple peer-reviewed research papers (PDF) to begin querying with RAG, running gap analysis, or generating reviews.
            </p>
          </div>
          <button
            onClick={onOpenUpload}
            className="academic-button-primary text-xs"
          >
            <Upload className="w-4 h-4" />
            <span>Upload Papers Now</span>
          </button>
        </div>
      )}

      {/* Paper Metadata Inspection Modal */}
      {viewPaper && (
        <Modal
          isOpen={!!viewPaper}
          onClose={() => setViewPaper(null)}
          title="Paper Bibliographic Details"
          maxWidth="max-w-3xl"
        >
          <div className="space-y-5">
            <div>
              <span className="text-[11px] font-bold uppercase tracking-wider text-academic-600 dark:text-academic-400">
                Academic Title
              </span>
              <h2 className="text-lg font-bold text-slate-900 dark:text-white mt-0.5">
                {viewPaper.title}
              </h2>
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 p-3 bg-slate-50 dark:bg-navy-950 rounded-xl text-xs">
              <div>
                <span className="text-slate-400">Authors</span>
                <p className="font-semibold text-slate-800 dark:text-slate-200">{viewPaper.authors || 'Unknown'}</p>
              </div>
              <div>
                <span className="text-slate-400">Publication Year</span>
                <p className="font-semibold text-slate-800 dark:text-slate-200">{viewPaper.publication_year || 'N/A'}</p>
              </div>
              <div>
                <span className="text-slate-400">Pages & Chunks</span>
                <p className="font-semibold text-slate-800 dark:text-slate-200">
                  {viewPaper.page_count} pages ({viewPaper.chunks_count || 'indexed'} chunks)
                </p>
              </div>
            </div>

            <div>
              <span className="text-[11px] font-bold uppercase tracking-wider text-slate-500">
                Abstract
              </span>
              <p className="mt-1 text-xs text-slate-700 dark:text-slate-300 leading-relaxed bg-slate-50 dark:bg-navy-950/60 p-4 rounded-xl border border-slate-200 dark:border-slate-800">
                {viewPaper.abstract || 'No abstract text extracted.'}
              </p>
            </div>

            {viewPaper.keywords && (
              <div>
                <span className="text-[11px] font-bold uppercase tracking-wider text-slate-500">
                  Extracted Keywords
                </span>
                <div className="flex flex-wrap gap-1.5 mt-1.5">
                  {viewPaper.keywords.split(',').map((kw, i) => (
                    <span 
                      key={i} 
                      className="text-xs px-2.5 py-1 rounded-md bg-academic-50 text-academic-700 dark:bg-academic-950 dark:text-academic-300 border border-academic-200 dark:border-academic-800 font-medium"
                    >
                      {kw.trim()}
                    </span>
                  ))}
                </div>
              </div>
            )}

            <div className="pt-2 flex justify-end">
              <button
                onClick={() => setViewPaper(null)}
                className="academic-button-secondary text-xs"
              >
                Close
              </button>
            </div>
          </div>
        </Modal>
      )}
    </div>
  );
}
