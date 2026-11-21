import React, { useState, useEffect } from 'react';
import { 
  GitCompare, 
  Check, 
  Loader2, 
  Sparkles, 
  BookOpen, 
  Trash2, 
  History, 
  Calendar,
  Layers,
  ArrowRight
} from 'lucide-react';
import { compareApi, papersApi } from '../api/client';
import { useProject } from '../contexts/ProjectContext';

export default function Comparison() {
  const { selectedProject } = useProject();
  const [papers, setPapers] = useState([]);
  const [selectedIds, setSelectedIds] = useState([]);
  const [customTitle, setCustomTitle] = useState('');
  const [isComparing, setIsComparing] = useState(false);
  const [activeComparison, setActiveComparison] = useState(null);
  const [history, setHistory] = useState([]);
  const [loadingHistory, setLoadingHistory] = useState(false);

  // Load project papers
  useEffect(() => {
    if (!selectedProject) return;
    const fetchPapers = async () => {
      try {
        const res = await papersApi.listByProject(selectedProject.id);
        setPapers(res.data);
      } catch (err) {
        console.error("Error loading papers for comparison:", err);
      }
    };
    fetchPapers();
    loadHistory();
  }, [selectedProject]);

  const loadHistory = async () => {
    if (!selectedProject) return;
    setLoadingHistory(true);
    try {
      const res = await compareApi.getHistory(selectedProject.id);
      setHistory(res.data);
      if (res.data.length > 0 && !activeComparison) {
        setActiveComparison(res.data[0]);
      }
    } catch (err) {
      console.error("Error loading comparison history:", err);
    } finally {
      setLoadingHistory(false);
    }
  };

  const toggleSelect = (id) => {
    setSelectedIds(prev => 
      prev.includes(id) ? prev.filter(pId => pId !== id) : [...prev, id]
    );
  };

  const handleRunComparison = async () => {
    if (selectedIds.length < 2) return;
    setIsComparing(true);
    try {
      const res = await compareApi.generate(
        selectedProject.id,
        selectedIds,
        customTitle || "Methodology & Findings Comparison Matrix"
      );
      setActiveComparison(res.data);
      setCustomTitle('');
      loadHistory();
    } catch (err) {
      console.error("Error generating comparison:", err);
      alert("Failed to generate comparison. Please check your papers and connection.");
    } finally {
      setIsComparing(false);
    }
  };

  const handleDeleteHistory = async (id, e) => {
    e.stopPropagation();
    try {
      await compareApi.delete(id);
      setHistory(prev => prev.filter(h => h.id !== id));
      if (activeComparison?.id === id) {
        setActiveComparison(null);
      }
    } catch (err) {
      console.error("Error deleting comparison:", err);
    }
  };

  const comparisonRows = [
    { key: 'research_objective', label: 'Research Objective' },
    { key: 'methodology', label: 'Methodology & Framework' },
    { key: 'algorithms', label: 'Algorithms & Models' },
    { key: 'datasets', label: 'Datasets & Benchmarks' },
    { key: 'metrics', label: 'Evaluation Metrics' },
    { key: 'results', label: 'Results & Findings' },
    { key: 'strengths', label: 'Strengths & Novelty' },
    { key: 'limitations', label: 'Limitations & Constraints' },
    { key: 'future_work', label: 'Future Research Directions' },
  ];

  return (
    <div className="p-4 sm:p-6 lg:p-8 space-y-6 sm:space-y-8 max-w-7xl mx-auto min-w-0">
      {/* Title Header */}
      <div>
        <h2 className="text-xl font-bold text-slate-900 dark:text-white flex items-center gap-2">
          <GitCompare className="w-5 h-5 text-academic-600" /> Research Paper Comparison Matrix
        </h2>
        <p className="text-xs text-slate-500 dark:text-slate-400">
          Select multiple research papers to evaluate objectives, algorithms, benchmarks, results, and limitations in a structured comparison table.
        </p>
      </div>

      {/* Paper Selection Card */}
      <div className="academic-card p-4 sm:p-6 space-y-4">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2 border-b border-slate-100 dark:border-slate-800 pb-3">
          <div className="flex items-center gap-2">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-500">
              Step 1: Select Papers to Compare
            </span>
            <span className="text-xs text-academic-600 font-semibold">
              ({selectedIds.length} of {papers.length} selected)
            </span>
          </div>
          <button
            onClick={() => {
              if (selectedIds.length === papers.length) setSelectedIds([]);
              else setSelectedIds(papers.map(p => p.id));
            }}
            className="text-xs text-academic-600 dark:text-academic-400 hover:underline font-medium"
          >
            {selectedIds.length === papers.length ? 'Deselect All' : 'Select All'}
          </button>
        </div>

        {papers.length > 0 ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3 max-h-56 overflow-y-auto p-1">
            {papers.map((p) => {
              const isSelected = selectedIds.includes(p.id);
              return (
                <div
                  key={p.id}
                  onClick={() => toggleSelect(p.id)}
                  className={`p-3 rounded-xl border text-xs cursor-pointer transition-all flex items-start gap-2.5 ${
                    isSelected
                      ? 'border-academic-500 bg-academic-50/70 dark:bg-academic-950/50 dark:border-academic-500'
                      : 'border-slate-200 dark:border-slate-800 bg-white dark:bg-navy-850 hover:border-slate-300'
                  }`}
                >
                  <div className={`w-4 h-4 rounded border mt-0.5 flex items-center justify-center shrink-0 ${
                    isSelected ? 'bg-academic-600 border-academic-600 text-white' : 'border-slate-300 dark:border-slate-600'
                  }`}>
                    {isSelected && <Check className="w-3 h-3" />}
                  </div>
                  <div className="overflow-hidden space-y-0.5">
                    <p className="font-semibold text-slate-900 dark:text-slate-100 truncate">{p.title}</p>
                    <p className="text-[11px] text-slate-500 truncate">{p.authors || 'Unknown'} ({p.publication_year || 'N/A'})</p>
                  </div>
                </div>
              );
            })}
          </div>
        ) : (
          <p className="text-xs text-slate-400 italic">No papers uploaded in this project yet.</p>
        )}

        {/* Action Controls */}
        <div className="pt-2 flex flex-col sm:flex-row items-center justify-between gap-3">
          <input
            type="text"
            placeholder="Comparison Title (optional)..."
            value={customTitle}
            onChange={(e) => setCustomTitle(e.target.value)}
            className="w-full sm:w-80 px-3 py-2 bg-slate-50 dark:bg-navy-950 border border-slate-200 dark:border-slate-800 rounded-lg text-xs text-slate-800 dark:text-slate-200 focus:outline-none"
          />

          <button
            onClick={handleRunComparison}
            disabled={selectedIds.length < 2 || isComparing}
            className="academic-button-primary text-xs w-full sm:w-auto"
          >
            {isComparing ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                <span>Cross-analyzing Papers with Gemini...</span>
              </>
            ) : (
              <>
                <Sparkles className="w-4 h-4" />
                <span>Generate Structured Comparison ({selectedIds.length} papers)</span>
              </>
            )}
          </button>
        </div>
      </div>

      {/* History Tabs */}
      {history.length > 0 && (
        <div className="flex items-center gap-2 overflow-x-auto pb-1">
          <span className="text-xs font-bold uppercase tracking-wider text-slate-400 shrink-0 flex items-center gap-1">
            <History className="w-3.5 h-3.5" /> Past Comparisons:
          </span>
          {history.map((h) => (
            <button
              key={h.id}
              onClick={() => setActiveComparison(h)}
              className={`shrink-0 text-xs px-3 py-1.5 rounded-lg border flex items-center gap-2 transition-all ${
                activeComparison?.id === h.id
                  ? 'bg-academic-600 text-white border-academic-600 font-semibold shadow-xs'
                  : 'bg-white dark:bg-navy-850 text-slate-600 dark:text-slate-300 border-slate-200 dark:border-slate-800 hover:bg-slate-50'
              }`}
            >
              <span className="truncate max-w-[200px]">{h.title}</span>
              <Trash2 
                onClick={(e) => handleDeleteHistory(h.id, e)}
                className="w-3 h-3 text-slate-400 hover:text-rose-500" 
              />
            </button>
          ))}
        </div>
      )}

      {/* Comparison Results Section */}
      {activeComparison ? (
        <div className="space-y-6">
          {/* Executive Summary Card */}
          {activeComparison.summary && (
            <div className="academic-card p-4 sm:p-6 bg-gradient-to-br from-academic-50/50 to-white dark:from-academic-950/30 dark:to-navy-900 border-academic-200/60 dark:border-academic-800/60 space-y-2">
              <span className="text-xs font-bold uppercase tracking-wider text-academic-700 dark:text-academic-400 flex items-center gap-1.5">
                <Sparkles className="w-4 h-4" /> Executive Comparative Synthesis
              </span>
              <p className="text-xs sm:text-sm text-slate-700 dark:text-slate-300 leading-relaxed whitespace-pre-line">
                {activeComparison.summary}
              </p>
            </div>
          )}

          {/* Structured Comparison Table */}
          <div className="academic-card overflow-hidden">
            <div className="p-4 border-b border-slate-100 dark:border-slate-800 flex items-center justify-between">
              <h3 className="font-bold text-sm text-slate-900 dark:text-white truncate">
                {activeComparison.title}
              </h3>
              <span className="text-[11px] text-slate-400 sm:hidden">Swipe horizontally →</span>
            </div>

            <div className="overflow-x-auto w-full">
              <table className="w-full text-xs text-left border-collapse min-w-[650px]">
                <thead>
                  <tr className="bg-slate-50 dark:bg-navy-950 border-b border-slate-200 dark:border-slate-800">
                    <th className="p-4 font-bold text-slate-600 dark:text-slate-400 w-44 shrink-0 uppercase tracking-wider text-[11px]">
                      Comparison Dimension
                    </th>
                    {activeComparison.comparison_data.map((item, idx) => (
                      <th key={idx} className="p-4 font-bold text-slate-900 dark:text-white min-w-[280px]">
                        <div className="space-y-0.5">
                          <p className="font-bold text-sm text-academic-700 dark:text-academic-400 line-clamp-2">
                            {item.paper_title}
                          </p>
                          <p className="text-[11px] font-normal text-slate-500">
                            {item.authors || 'Unknown'} {item.publication_year ? `(${item.publication_year})` : ''}
                          </p>
                        </div>
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
                  {comparisonRows.map((row) => (
                    <tr key={row.key} className="hover:bg-slate-50/50 dark:hover:bg-navy-850/50 transition-colors">
                      <td className="p-4 font-bold text-slate-700 dark:text-slate-300 bg-slate-50/30 dark:bg-navy-950/30 align-top">
                        {row.label}
                      </td>
                      {activeComparison.comparison_data.map((item, idx) => (
                        <td key={idx} className="p-4 text-slate-600 dark:text-slate-300 leading-relaxed align-top">
                          {item[row.key] || <span className="text-slate-400 italic">Not specified</span>}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      ) : (
        <div className="academic-card p-12 text-center space-y-3">
          <GitCompare className="w-10 h-10 text-slate-300 dark:text-slate-700 mx-auto" />
          <p className="text-xs text-slate-500">
            Select 2 or more research papers above and click "Generate Structured Comparison" to view a multi-dimensional matrix.
          </p>
        </div>
      )}
    </div>
  );
}
