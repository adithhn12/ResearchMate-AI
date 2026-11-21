import React, { useState, useEffect } from 'react';
import { 
  FileText, 
  Sparkles, 
  Download, 
  Edit3, 
  Save, 
  Check, 
  Loader2, 
  History, 
  Trash2, 
  FileDown,
  BookOpen
} from 'lucide-react';
import { reviewsApi, papersApi } from '../api/client';
import { useProject } from '../contexts/ProjectContext';

export default function LiteratureReview() {
  const { selectedProject } = useProject();
  const [papers, setPapers] = useState([]);
  const [selectedIds, setSelectedIds] = useState([]);
  const [reviewTitle, setReviewTitle] = useState('');
  const [researchFocus, setResearchFocus] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [activeReview, setActiveReview] = useState(null);
  const [history, setHistory] = useState([]);
  const [loadingHistory, setLoadingHistory] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const [editedData, setEditedData] = useState({});
  const [isSaving, setIsSaving] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);

  useEffect(() => {
    if (!selectedProject) return;
    const fetchPapers = async () => {
      try {
        const res = await papersApi.listByProject(selectedProject.id);
        setPapers(res.data);
      } catch (err) {
        console.error("Error loading papers for literature review:", err);
      }
    };
    fetchPapers();
    loadHistory();
  }, [selectedProject]);

  const loadHistory = async () => {
    if (!selectedProject) return;
    setLoadingHistory(true);
    try {
      const res = await reviewsApi.listByProject(selectedProject.id);
      setHistory(res.data);
      if (res.data.length > 0 && !activeReview) {
        selectReview(res.data[0]);
      }
    } catch (err) {
      console.error("Error loading review history:", err);
    } finally {
      setLoadingHistory(false);
    }
  };

  const selectReview = (rev) => {
    setActiveReview(rev);
    setEditedData({
      title: rev.title,
      introduction: rev.introduction,
      background_related_work: rev.background_related_work,
      thematic_analysis: rev.thematic_analysis,
      comparison_existing_approaches: rev.comparison_existing_approaches,
      research_limitations: rev.research_limitations,
      research_gaps: rev.research_gaps,
      conclusion: rev.conclusion,
      references: rev.references,
    });
    setIsEditing(false);
  };

  const toggleSelect = (id) => {
    setSelectedIds(prev => 
      prev.includes(id) ? prev.filter(pId => pId !== id) : [...prev, id]
    );
  };

  const handleGenerate = async () => {
    if (selectedIds.length === 0) return;
    setIsGenerating(true);
    try {
      const res = await reviewsApi.generate(
        selectedProject.id,
        selectedIds,
        reviewTitle || "Comprehensive Literature Review & Meta-Synthesis",
        researchFocus || ""
      );
      selectReview(res.data);
      loadHistory();
    } catch (err) {
      console.error("Error generating literature review:", err);
      alert("Failed to generate literature review. Please try again.");
    } finally {
      setIsGenerating(false);
    }
  };

  const handleSaveEdits = async () => {
    if (!activeReview) return;
    setIsSaving(true);
    try {
      const res = await reviewsApi.update(activeReview.id, editedData);
      setActiveReview(res.data);
      setIsEditing(false);
      setSaveSuccess(true);
      setTimeout(() => setSaveSuccess(false), 3000);
      loadHistory();
    } catch (err) {
      console.error("Error saving edits:", err);
    } finally {
      setIsSaving(false);
    }
  };

  const handleDeleteReview = async (id, e) => {
    e.stopPropagation();
    try {
      await reviewsApi.delete(id);
      setHistory(prev => prev.filter(r => r.id !== id));
      if (activeReview?.id === id) {
        setActiveReview(null);
      }
    } catch (err) {
      console.error("Error deleting review:", err);
    }
  };

  const sections = [
    { key: 'introduction', label: '1. Introduction' },
    { key: 'background_related_work', label: '2. Background and Related Work' },
    { key: 'thematic_analysis', label: '3. Thematic Literature Analysis' },
    { key: 'comparison_existing_approaches', label: '4. Comparison of Existing Approaches' },
    { key: 'research_limitations', label: '5. Research Limitations' },
    { key: 'research_gaps', label: '6. Research Gaps & Open Problems' },
    { key: 'conclusion', label: '7. Conclusion & Future Outlook' },
    { key: 'references', label: '8. References (APA Style)' },
  ];

  return (
    <div className="p-4 sm:p-6 lg:p-8 space-y-6 sm:space-y-8 max-w-7xl mx-auto min-w-0">
      {/* Header */}
      <div>
        <h2 className="text-xl font-bold text-slate-900 dark:text-white flex items-center gap-2">
          <FileText className="w-5 h-5 text-academic-600" /> Automated Literature Review Generator
        </h2>
        <p className="text-xs text-slate-500 dark:text-slate-400">
          Synthesize selected research papers into a publication-ready academic literature review with in-place editing and DOCX/PDF export.
        </p>
      </div>

      {/* Generation Setup Card */}
      <div className="academic-card p-4 sm:p-6 space-y-4">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2 border-b border-slate-100 dark:border-slate-800 pb-3">
          <div className="flex items-center gap-2">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-500">
              Select Papers to Synthesize
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

        {/* Form Inputs */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3 pt-2">
          <input
            type="text"
            placeholder="Review Title (e.g. Advancements in RAG & Multi-Agent Literature)..."
            value={reviewTitle}
            onChange={(e) => setReviewTitle(e.target.value)}
            className="px-3.5 py-2 bg-slate-50 dark:bg-navy-950 border border-slate-200 dark:border-slate-800 rounded-lg text-xs text-slate-800 dark:text-slate-200 focus:outline-none"
          />
          <input
            type="text"
            placeholder="Optional Specific Research Focus / Sub-domain..."
            value={researchFocus}
            onChange={(e) => setResearchFocus(e.target.value)}
            className="px-3.5 py-2 bg-slate-50 dark:bg-navy-950 border border-slate-200 dark:border-slate-800 rounded-lg text-xs text-slate-800 dark:text-slate-200 focus:outline-none"
          />
        </div>

        <div className="pt-2 flex justify-end">
          <button
            onClick={handleGenerate}
            disabled={selectedIds.length === 0 || isGenerating}
            className="academic-button-primary text-xs w-full sm:w-auto"
          >
            {isGenerating ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                <span>Generating 8-Section Literature Review with Gemini...</span>
              </>
            ) : (
              <>
                <Sparkles className="w-4 h-4" />
                <span>Generate Literature Review ({selectedIds.length} papers)</span>
              </>
            )}
          </button>
        </div>
      </div>

      {/* History Tabs */}
      {history.length > 0 && (
        <div className="flex items-center gap-2 overflow-x-auto pb-1">
          <span className="text-xs font-bold uppercase tracking-wider text-slate-400 shrink-0 flex items-center gap-1">
            <History className="w-3.5 h-3.5" /> Saved Reviews:
          </span>
          {history.map((rev) => (
            <button
              key={rev.id}
              onClick={() => selectReview(rev)}
              className={`shrink-0 text-xs px-3 py-1.5 rounded-lg border flex items-center gap-2 transition-all ${
                activeReview?.id === rev.id
                  ? 'bg-academic-600 text-white border-academic-600 font-semibold shadow-sm'
                  : 'bg-white dark:bg-navy-850 text-slate-600 dark:text-slate-300 border-slate-200 dark:border-slate-800 hover:bg-slate-50'
              }`}
            >
              <span className="truncate max-w-[200px]">{rev.title}</span>
              <Trash2 
                onClick={(e) => handleDeleteReview(rev.id, e)}
                className="w-3 h-3 text-slate-400 hover:text-rose-500" 
              />
            </button>
          ))}
        </div>
      )}

      {/* Review Document View */}
      {activeReview ? (
        <div className="academic-card overflow-hidden">
          {/* Top Document Toolbar */}
          <div className="p-4 bg-slate-50 dark:bg-navy-950 border-b border-slate-200 dark:border-slate-800 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
            <div>
              <h3 className="font-bold text-base text-slate-900 dark:text-white">
                {activeReview.title}
              </h3>
              <p className="text-xs text-slate-500">
                Created: {new Date(activeReview.created_at).toLocaleDateString()}
              </p>
            </div>

            <div className="flex flex-wrap items-center gap-2">
              {/* Edit Mode Toggle */}
              {isEditing ? (
                <button
                  onClick={handleSaveEdits}
                  disabled={isSaving}
                  className="academic-button-primary text-xs py-1.5 px-3 bg-emerald-600 hover:bg-emerald-700"
                >
                  {isSaving ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Save className="w-3.5 h-3.5" />}
                  <span>Save Changes</span>
                </button>
              ) : (
                <button
                  onClick={() => setIsEditing(true)}
                  className="academic-button-secondary text-xs py-1.5 px-3"
                >
                  <Edit3 className="w-3.5 h-3.5 text-academic-500" />
                  <span>Edit Review</span>
                </button>
              )}

              {saveSuccess && (
                <span className="text-xs text-emerald-600 font-semibold flex items-center gap-1">
                  <Check className="w-3.5 h-3.5" /> Saved!
                </span>
              )}

              {/* Export Buttons */}
              <a
                href={reviewsApi.exportDocxUrl(activeReview.id)}
                download
                className="academic-button-secondary text-xs py-1.5 px-3 flex items-center gap-1.5 hover:text-blue-600"
                title="Download formatted Microsoft Word document (.docx)"
              >
                <FileDown className="w-3.5 h-3.5 text-blue-500" />
                <span>Export DOCX</span>
              </a>

              <a
                href={reviewsApi.exportPdfUrl(activeReview.id)}
                download
                className="academic-button-secondary text-xs py-1.5 px-3 flex items-center gap-1.5 hover:text-rose-600"
                title="Download publication-ready PDF document (.pdf)"
              >
                <Download className="w-3.5 h-3.5 text-rose-500" />
                <span>Export PDF</span>
              </a>
            </div>
          </div>

          {/* Document Content Paper Page */}
          <div className="p-4 sm:p-8 md:p-12 space-y-6 sm:space-y-8 bg-white dark:bg-navy-900 max-w-4xl mx-auto font-serif">
            {sections.map((sec) => (
              <div key={sec.key} className="space-y-3">
                <h4 className="text-base font-bold font-sans text-academic-800 dark:text-academic-400 border-b border-slate-100 dark:border-slate-800 pb-1.5">
                  {sec.label}
                </h4>

                {isEditing ? (
                  <textarea
                    rows={6}
                    value={editedData[sec.key] || ''}
                    onChange={(e) => setEditedData({ ...editedData, [sec.key]: e.target.value })}
                    className="w-full text-xs font-sans p-3 rounded-lg border border-slate-300 dark:border-slate-700 bg-slate-50 dark:bg-navy-950 text-slate-800 dark:text-slate-200 focus:outline-none focus:ring-1 focus:ring-academic-500 leading-relaxed"
                  />
                ) : (
                  <div className="text-xs sm:text-sm text-slate-700 dark:text-slate-300 leading-relaxed whitespace-pre-wrap">
                    {activeReview[sec.key] || <span className="text-slate-400 italic">No content available.</span>}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      ) : (
        <div className="academic-card p-12 text-center space-y-3">
          <FileText className="w-10 h-10 text-slate-300 dark:text-slate-700 mx-auto" />
          <p className="text-xs text-slate-500">
            Select research papers above and click "Generate Literature Review" to create an 8-section synthesis with DOCX/PDF export.
          </p>
        </div>
      )}
    </div>
  );
}
