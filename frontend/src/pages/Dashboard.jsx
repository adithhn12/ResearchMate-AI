import React, { useState, useEffect } from 'react';
import { 
  BookOpen, 
  Layers, 
  MessageSquare, 
  GitCompare, 
  FileText, 
  Clock, 
  ArrowUpRight, 
  FileUp, 
  Sparkles,
  CheckCircle2,
  AlertCircle,
  Loader2
} from 'lucide-react';
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  Tooltip, 
  ResponsiveContainer, 
  PieChart, 
  Pie, 
  Cell 
} from 'recharts';
import { analyticsApi } from '../api/client';
import { useProject } from '../contexts/ProjectContext';

const STATUS_COLORS = {
  Indexed: '#10b981', // green
  Processing: '#3b82f6', // blue
  Failed: '#ef4444', // red
  Uploaded: '#f59e0b', // amber
};

export default function Dashboard({ setActiveTab, onOpenUpload }) {
  const { selectedProject } = useProject();
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchStats = async () => {
      setLoading(true);
      try {
        const res = await analyticsApi.getDashboard(selectedProject?.id);
        setAnalytics(res.data);
      } catch (err) {
        console.error("Dashboard analytics error:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchStats();
  }, [selectedProject]);

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center h-96 gap-3">
        <Loader2 className="w-8 h-8 text-academic-600 animate-spin" />
        <p className="text-sm text-slate-500">Loading research intelligence...</p>
      </div>
    );
  }

  const statCards = [
    { label: 'Total Papers', value: analytics?.total_papers || 0, icon: BookOpen, color: 'text-blue-500', bg: 'bg-blue-50 dark:bg-blue-950/40' },
    { label: 'Research Projects', value: analytics?.total_projects || 0, icon: Layers, color: 'text-indigo-500', bg: 'bg-indigo-50 dark:bg-indigo-950/40' },
    { label: 'AI Inquiries', value: analytics?.total_chat_sessions || 0, icon: MessageSquare, color: 'text-teal-500', bg: 'bg-teal-50 dark:bg-teal-950/40' },
    { label: 'Methodology Comparisons', value: analytics?.total_comparisons || 0, icon: GitCompare, color: 'text-amber-500', bg: 'bg-amber-50 dark:bg-amber-950/40' },
  ];

  return (
    <div className="p-4 sm:p-6 lg:p-8 space-y-6 sm:space-y-8 max-w-7xl mx-auto min-w-0">
      {/* Top Banner / Welcome */}
      <div className="p-5 sm:p-6 rounded-2xl bg-gradient-to-r from-academic-900 via-academic-800 to-navy-900 text-white shadow-lg relative overflow-hidden border border-academic-700/30">
        <div className="relative z-10 max-w-2xl space-y-2">
          <div className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-academic-500/20 text-academic-300 text-xs font-semibold border border-academic-400/20">
            <Sparkles className="w-3.5 h-3.5" /> AI Academic Research Assistant
          </div>
          <h2 className="text-xl sm:text-2xl font-extrabold tracking-tight">
            Accelerate Your Academic Literature Research
          </h2>
          <p className="text-xs sm:text-sm text-slate-300 leading-relaxed">
            Ingest multiple peer-reviewed papers, query with grounded page citations, and contrast research methodologies side-by-side in seconds.
          </p>
          <div className="pt-2 flex flex-wrap gap-2.5 sm:gap-3">
            <button
              onClick={onOpenUpload}
              className="px-3.5 sm:px-4 py-2 bg-academic-500 hover:bg-academic-600 text-white rounded-lg text-xs font-semibold flex items-center gap-2 shadow-sm transition-all"
            >
              <FileUp className="w-4 h-4" />
              Upload Papers
            </button>
            <button
              onClick={() => setActiveTab('assistant')}
              className="px-3.5 sm:px-4 py-2 bg-white/10 hover:bg-white/20 text-white rounded-lg text-xs font-semibold flex items-center gap-2 border border-white/10 transition-all"
            >
              <MessageSquare className="w-4 h-4" />
              Ask AI Assistant
            </button>
          </div>
        </div>
      </div>

      {/* Metrics Row */}
      <div className="grid grid-cols-2 sm:grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4">
        {statCards.map((stat, i) => {
          const Icon = stat.icon;
          return (
            <div key={i} className="academic-card p-3.5 sm:p-4 space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-[11px] sm:text-xs font-medium text-slate-500 dark:text-slate-400 truncate">{stat.label}</span>
                <div className={`p-1.5 sm:p-2 rounded-lg ${stat.bg} shrink-0`}>
                  <Icon className={`w-3.5 h-3.5 sm:w-4 sm:h-4 ${stat.color}`} />
                </div>
              </div>
              <p className="text-xl sm:text-2xl font-bold text-slate-900 dark:text-white">{stat.value}</p>
            </div>
          );
        })}
      </div>

      {/* Analytics Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 sm:gap-6 min-w-0">
        {/* Papers by Publication Year */}
        <div className="academic-card p-4 sm:p-6 space-y-4 min-w-0 overflow-hidden">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="font-bold text-xs sm:text-sm text-slate-900 dark:text-white">Publications by Year</h3>
              <p className="text-[11px] sm:text-xs text-slate-500">Distribution of indexed literature across timeline</p>
            </div>
          </div>
          <div className="h-56 sm:h-64 w-full min-w-0">
            {analytics?.papers_by_year && analytics.papers_by_year.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={analytics.papers_by_year} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                  <XAxis dataKey="year" stroke="#94a3b8" fontSize={11} tickLine={false} />
                  <YAxis stroke="#94a3b8" fontSize={11} tickLine={false} allowDecimals={false} />
                  <Tooltip 
                    contentStyle={{ 
                      backgroundColor: '#0f172a', 
                      borderColor: '#334155', 
                      borderRadius: '8px', 
                      color: '#fff',
                      fontSize: '12px' 
                    }} 
                  />
                  <Bar dataKey="count" fill="#3b82f6" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-full flex items-center justify-center text-xs text-slate-400 italic">
                No publication year data available yet. Upload papers to view timeline distribution.
              </div>
            )}
          </div>
        </div>

        {/* Ingestion & Processing Status */}
        <div className="academic-card p-4 sm:p-6 space-y-4 min-w-0 overflow-hidden">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="font-bold text-xs sm:text-sm text-slate-900 dark:text-white">Document Processing Status</h3>
              <p className="text-[11px] sm:text-xs text-slate-500">Vector indexing and chunk extraction status</p>
            </div>
          </div>
          <div className="h-56 sm:h-64 w-full flex items-center justify-center min-w-0">
            {analytics?.status_distribution && analytics.status_distribution.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={analytics.status_distribution}
                    cx="50%"
                    cy="50%"
                    innerRadius={50}
                    outerRadius={75}
                    paddingAngle={4}
                    dataKey="count"
                    nameKey="status"
                    label={({ status, count }) => `${status}: ${count}`}
                  >
                    {analytics.status_distribution.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={STATUS_COLORS[entry.status] || '#64748b'} />
                    ))}
                  </Pie>
                  <Tooltip 
                    contentStyle={{ 
                      backgroundColor: '#0f172a', 
                      borderColor: '#334155', 
                      borderRadius: '8px', 
                      color: '#fff',
                      fontSize: '12px' 
                    }} 
                  />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <div className="text-xs text-slate-400 italic">
                No document ingestion status to display.
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Two Column Layout: Recent Uploads & Activity Timeline */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 sm:gap-6 min-w-0">
        {/* Recent Uploads (2 cols) */}
        <div className="lg:col-span-2 academic-card p-6 space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="font-bold text-sm text-slate-900 dark:text-white">Recent Literature Uploads</h3>
              <p className="text-xs text-slate-500">Recently indexed papers ready for RAG and synthesis</p>
            </div>
            <button
              onClick={() => setActiveTab('library')}
              className="text-xs text-academic-600 dark:text-academic-400 font-semibold hover:underline flex items-center gap-1"
            >
              View Library <ArrowUpRight className="w-3.5 h-3.5" />
            </button>
          </div>

          {analytics?.recent_uploads && analytics.recent_uploads.length > 0 ? (
            <div className="divide-y divide-slate-100 dark:divide-slate-800">
              {analytics.recent_uploads.map((paper) => (
                <div key={paper.id} className="py-3 flex items-start justify-between gap-4">
                  <div className="space-y-1">
                    <p className="text-sm font-semibold text-slate-900 dark:text-slate-100 line-clamp-1">
                      {paper.title}
                    </p>
                    <p className="text-xs text-slate-500 line-clamp-1">
                      {paper.authors || 'Unknown Authors'} • {paper.publication_year || 'N/A'} • {paper.page_count} pages
                    </p>
                  </div>
                  <span className={`shrink-0 inline-flex items-center gap-1 text-[11px] font-medium px-2 py-0.5 rounded-full ${
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
                </div>
              ))}
            </div>
          ) : (
            <div className="py-12 text-center space-y-3">
              <BookOpen className="w-8 h-8 text-slate-300 dark:text-slate-700 mx-auto" />
              <p className="text-xs text-slate-500">No papers uploaded yet in this project.</p>
              <button
                onClick={onOpenUpload}
                className="academic-button-primary text-xs py-1.5 px-3"
              >
                Upload Your First Paper
              </button>
            </div>
          )}
        </div>

        {/* Activity Stream (1 col) */}
        <div className="academic-card p-6 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="font-bold text-sm text-slate-900 dark:text-white flex items-center gap-1.5">
              <Clock className="w-4 h-4 text-slate-400" /> Research Activity
            </h3>
          </div>

          {analytics?.recent_activities && analytics.recent_activities.length > 0 ? (
            <div className="space-y-4">
              {analytics.recent_activities.map((act) => (
                <div key={act.id} className="flex gap-3 text-xs">
                  <div className="w-1.5 h-1.5 rounded-full bg-academic-500 mt-1.5 shrink-0" />
                  <div className="space-y-0.5">
                    <p className="text-slate-800 dark:text-slate-200 font-medium">
                      {act.details}
                    </p>
                    <p className="text-[10px] text-slate-400">
                      {new Date(act.created_at).toLocaleDateString()} {new Date(act.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-xs text-slate-400 italic">No recent activity logged.</p>
          )}
        </div>
      </div>
    </div>
  );
}
