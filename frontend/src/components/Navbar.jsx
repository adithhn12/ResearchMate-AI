import React from 'react';
import { Layers, Upload, MessageSquare, Menu } from 'lucide-react';
import { useProject } from '../contexts/ProjectContext';

export default function Navbar({ activeTab, setActiveTab, onOpenUpload, onToggleSidebar }) {
  const { selectedProject } = useProject();

  const getTitle = () => {
    switch (activeTab) {
      case 'dashboard': return 'Dashboard & Analytics';
      case 'library': return 'Paper Library';
      case 'assistant': return 'AI Research Assistant';
      case 'comparison': return 'Paper Comparison';
      case 'gaps': return 'Research Gap Analyzer';
      case 'reviews': return 'Literature Reviews';
      default: return 'ResearchMate AI';
    }
  };

  return (
    <header className="h-16 bg-white dark:bg-navy-900 border-b border-slate-200 dark:border-slate-800 px-4 sm:px-6 flex items-center justify-between transition-colors duration-200 shrink-0">
      <div className="flex items-center gap-3">
        {/* Mobile Hamburger Menu Toggle */}
        <button
          onClick={onToggleSidebar}
          className="p-2 -ml-1 rounded-lg text-slate-500 hover:text-slate-800 dark:text-slate-400 dark:hover:text-white hover:bg-slate-100 dark:hover:bg-navy-800 lg:hidden transition-colors"
          title="Open Navigation"
        >
          <Menu className="w-5 h-5" />
        </button>

        <div>
          <h2 className="text-base sm:text-lg font-bold text-slate-900 dark:text-white tracking-tight truncate max-w-[200px] sm:max-w-md">
            {getTitle()}
          </h2>
          {selectedProject && (
            <div className="flex items-center gap-1.5 text-[11px] sm:text-xs text-slate-500 dark:text-slate-400 truncate max-w-[200px] sm:max-w-md">
              <Layers className="w-3 h-3 text-academic-500 shrink-0" />
              <span className="hidden sm:inline">Active Project:</span>
              <span className="font-semibold text-slate-700 dark:text-slate-200 truncate">{selectedProject.name}</span>
            </div>
          )}
        </div>
      </div>

      <div className="flex items-center gap-2 sm:gap-3">
        {onOpenUpload && (
          <button
            onClick={onOpenUpload}
            className="academic-button-primary text-xs py-1.5 px-2.5 sm:px-3"
            title="Upload Academic Papers"
          >
            <Upload className="w-3.5 h-3.5" />
            <span className="hidden sm:inline">Upload Papers</span>
          </button>
        )}
        {activeTab !== 'assistant' && (
          <button
            onClick={() => setActiveTab('assistant')}
            className="academic-button-secondary text-xs py-1.5 px-2.5 sm:px-3"
            title="Open AI Assistant"
          >
            <MessageSquare className="w-3.5 h-3.5 text-academic-500" />
            <span className="hidden sm:inline">Ask AI</span>
          </button>
        )}
      </div>
    </header>
  );
}
