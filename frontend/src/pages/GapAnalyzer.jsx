import React, { useState, useEffect } from 'react';
import { 
  Compass, 
  Sparkles, 
  AlertTriangle, 
  Lightbulb, 
  ArrowRight, 
  Check, 
  Loader2, 
  BookOpen, 
  Trash2, 
  History,
  Tag
} from 'lucide-react';
import { gapsApi, papersApi } from '../api/client';
import { useProject } from '../contexts/ProjectContext';

export default function GapAnalyzer() {
  const { selectedProject } = useProject();
  const [papers, setPapers] = useState([]);
  const [selectedIds, setSelectedIds] = useState([]);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [activeReport, setActiveReport] = useState(null);
  const [history, setHistory] = useState([]);
  const [loadingHistory, setLoadingHistory] = useState(false);
  const [filterType, setFilterType] = useState('all'); // 'all', 'explicit_limitation', 'ai_inferred_gap'

  useEffect(() => {
    if (!selectedProject) return;
    const fetchPapers = async () => {
      try {
        const res = await papersApi.listByProject(selectedProject.id);
        setPapers(res.data);
      } catch (err) {
        console.error("Error loading papers for gap analyzer:", err);
      }
    };
    fetchPapers();
    loadHistory();
  }, [selectedProject]);

  const loadHistory = async () => {
    if (!selectedProject) return;
    setLoadingHistory(true);
    try {
      const res = await gapsApi.getHistory(selectedProject.id);
      setHistory(res.data);
      if (res.data.length > 0 && !activeReport) {
        setActiveReport(res.data[0]);
      }
    } catch (err) {
      console.error("Error loading gap history:", err);
    } finally {
      setLoadingHistory(false);
    }
  };

  const toggleSelect = (id) => {
    setSelectedIds(prev => 
      prev.includes(id) ? prev.filter(pId => pId !== id) : [...prev, id]
    );
  };

  const handleRunAnalysis = async () => {
    if (selectedIds.length === 0) return;
    setIsAnalyzing(true);
    try {
      const res = await gapsApi.analyze(
        selectedProject.id,
        selectedIds,
        `Research Gap & Opportunity Report (${selectedIds.length} Papers)`
      );
      setActiveReport(res.data);
      loadHistory();
    } catch (err) {
      console.error("Error analyzing gaps:", err);
      alert("Failed to analyze research gaps. Please check your papers.");
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleDeleteHistory = async (id, e) => {
    e.stopPropagation();
    try {
      await gapsApi.delete(id);
      setHistory(prev => prev.filter(h => h.id !== id));
      if (activeReport?.id === id) {
        setActiveReport(null);
      }
    } catch (err) {
      console.error("Error deleting gap report:", err);
    }
  };

  const displayedGaps = activeReport?.gaps.filter(g => {
    if (filterType === 'all') return true;
    return g.type === filterType;
  }) || [];

  return (
    <div className="p-4 sm:p-6 lg:p-8 space-y-6 sm:space-y-8 max-w-7xl mx-auto min-w-0">
      {/* Title */}
      <div>
        <h2 className="text-xl font-bold text-slate-900 dark:text-white flex items-center gap-2">
          <Compass className="w-5 h-5 text-academic-600" /> Research Gap & Limitation Analyzer
        </h2>
        <p className="text-xs text-slate-500 dark:text-slate-400">
          Synthesize paper limitations, extract recurring academic challenges, and discover unexplored research opportunities with grounded references.
        </p>
      </div>

      {/* Paper Selection Card */}
      <div className="academic-card p-4 sm:p-6 space-y-4">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2 border-b border-slate-100 dark:border-slate-800 pb-3">
          <div className="flex items-center gap-2">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-500">
              Select Literature Corpus to Analyze
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

        <div className="pt-2 flex justify-end">
          <button
            onClick={handleRunAnalysis}
            disabled={selectedIds.length === 0 || isAnalyzing}
            className="academic-button-primary text-xs w-full sm:w-auto"
          >
            {isAnalyzing ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                <span>Extracting Limitations & Synthesizing Gaps...</span>
              </>
            ) : (
              <>
                <Sparkles className="w-4 h-4" />
                <span>Analyze Gaps & Future Directions ({selectedIds.length} papers)</span>
              </>
            )}
          </button>
        </div>
      </div>

      {/* History Tabs */}
      {history.length > 0 && (
        <div className="flex items-center gap-2 overflow-x-auto pb-1">
          <span className="text-xs font-bold uppercase tracking-wider text-slate-400 shrink-0 flex items-center gap-1">
            <History className="w-3.5 h-3.5" /> Past Analyses:
          </span>
          {history.map((h) => (
            <button
              key={h.id}
              onClick={() => setActiveReport(h)}
              className={`shrink-0 text-xs px-3 py-1.5 rounded-lg border flex items-center gap-2 transition-all ${
                activeReport?.id === h.id
                  ? 'bg-academic-600 text-white border-academic-600 font-semibold shadow-sm'
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

      {/* Active Gap Report */}
      {activeReport ? (
        <div className="space-y-6">
          {/* Recurring Challenges Banner */}
          {activeReport.recurring_challenges && activeReport.recurring_challenges.length > 0 && (
            <div className="academic-card p-6 bg-amber-50/50 dark:bg-amber-950/20 border-amber-200 dark:border-amber-900/40 space-y-3">
              <span className="text-xs font-bold uppercase tracking-wider text-amber-700 dark:text-amber-400 flex items-center gap-1.5">
                <AlertTriangle className="w-4 h-4" /> Recurring Cross-Literature Challenges
              </span>
              <ul className="space-y-2 text-xs text-amber-900 dark:text-amber-200">
                {activeReport.recurring_challenges.map((ch, idx) => (
                  <li key={idx} className="flex items-start gap-2">
                    <span className="w-1.5 h-1.5 rounded-full bg-amber-500 mt-1.5 shrink-0" />
                    <span>{ch}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Filter Pills */}
          <div className="flex items-center justify-between">
            <h3 className="font-bold text-sm text-slate-900 dark:text-white">
              Identified Limitations & Research Opportunities ({displayedGaps.length})
            </h3>
            <div className="flex items-center gap-1.5 bg-slate-100 dark:bg-navy-950 p-1 rounded-lg text-xs">
              <button
                onClick={() => setFilterType('all')}
                className={`px-2.5 py-1 rounded-md font-medium transition-colors ${
                  filterType === 'all' ? 'bg-white dark:bg-navy-850 text-slate-900 dark:text-white shadow-xs' : 'text-slate-500'
                }`}
              >
                All
              </button>
              <button
                onClick={() => setFilterType('explicit_limitation')}
                className={`px-2.5 py-1 rounded-md font-medium transition-colors ${
                  filterType === 'explicit_limitation' ? 'bg-white dark:bg-navy-850 text-amber-600 dark:text-amber-400 shadow-xs' : 'text-slate-500'
                }`}
              >
                Explicit Limitations
              </button>
              <button
                onClick={() => setFilterType('ai_inferred_gap')}
                className={`px-2.5 py-1 rounded-md font-medium transition-colors ${
                  filterType === 'ai_inferred_gap' ? 'bg-white dark:bg-navy-850 text-academic-600 dark:text-academic-400 shadow-xs' : 'text-slate-500'
                }`}
              >
                AI Inferred Gaps
              </button>
            </div>
          </div>

          {/* Gaps List Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {displayedGaps.map((gap, idx) => {
              const isExplicit = gap.type === 'explicit_limitation';
              return (
                <div
                  key={idx}
                  className="academic-card p-5 space-y-3 flex flex-col justify-between hover:border-academic-400 dark:hover:border-academic-700 transition-all"
                >
                  <div className="space-y-2">
                    {/* Badge header */}
                    <div className="flex items-center justify-between gap-2">
                      <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full uppercase tracking-wider ${
                        isExplicit
                          ? 'bg-amber-100 text-amber-800 dark:bg-amber-950/80 dark:text-amber-300 border border-amber-300 dark:border-amber-800'
                          : 'bg-indigo-100 text-indigo-800 dark:bg-indigo-950/80 dark:text-indigo-300 border border-indigo-300 dark:border-indigo-800'
                      }`}>
                        {isExplicit ? 'Explicit Author Limitation' : 'AI Inferred Research Gap'}
                      </span>
                      <span className="text-[10px] text-slate-400 font-semibold">
                        {gap.category}
                      </span>
                    </div>

                    {/* Title */}
                    <h4 className="font-bold text-sm text-slate-900 dark:text-white">
                      {gap.title}
                    </h4>

                    {/* Description */}
                    <p className="text-xs text-slate-600 dark:text-slate-300 leading-relaxed">
                      {gap.description}
                    </p>
                  </div>

                  {/* Future Direction Recommendation */}
                  <div className="space-y-2 pt-3 border-t border-slate-100 dark:border-slate-800">
                    <div className="p-3 bg-slate-50 dark:bg-navy-950 rounded-xl space-y-1">
                      <span className="text-[10px] font-bold uppercase tracking-wider text-academic-600 dark:text-academic-400 flex items-center gap-1">
                        <Lightbulb className="w-3.5 h-3.5" /> Proposed Future Research Direction
                      </span>
                      <p className="text-xs text-slate-700 dark:text-slate-200">
                        {gap.future_direction}
                      </p>
                    </div>

                    {/* Supporting Papers */}
                    {gap.supporting_papers && gap.supporting_papers.length > 0 && (
                      <div className="flex flex-wrap items-center gap-1.5 pt-1">
                        <span className="text-[10px] text-slate-400">Supporting Literature:</span>
                        {gap.supporting_papers.map((sp, sIdx) => (
                          <span
                            key={sIdx}
                            className="inline-flex items-center gap-1 text-[10px] font-medium px-2 py-0.5 rounded bg-slate-100 dark:bg-navy-850 text-slate-600 dark:text-slate-300"
                          >
                            <BookOpen className="w-2.5 h-2.5 text-academic-500" />
                            <span className="truncate max-w-[130px]">{sp.paper_title}</span>
                            {sp.page && <span className="font-bold text-academic-600">p. {sp.page}</span>}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      ) : (
        <div className="academic-card p-12 text-center space-y-3">
          <Compass className="w-10 h-10 text-slate-300 dark:text-slate-700 mx-auto" />
          <p className="text-xs text-slate-500">
            Select papers and run Gap Analysis to discover research limitations and future directions.
          </p>
        </div>
      )}
    </div>
  );
}
