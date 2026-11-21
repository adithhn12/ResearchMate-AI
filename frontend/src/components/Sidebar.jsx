import React, { useState } from 'react';
import { 
  LayoutDashboard, 
  BookOpen, 
  Bot, 
  GitCompare, 
  Compass, 
  FileText, 
  FolderPlus, 
  LogOut, 
  Sun, 
  Moon, 
  Layers, 
  Sparkles,
  X
} from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { useProject } from '../contexts/ProjectContext';
import { useTheme } from '../contexts/ThemeContext';

export default function Sidebar({ activeTab, setActiveTab, isOpen, onClose }) {
  const { user, logout } = useAuth();
  const { projects, selectedProject, setSelectedProject, createProject } = useProject();
  const { isDark, toggleTheme } = useTheme();
  const [showNewProject, setShowNewProject] = useState(false);
  const [newProjName, setNewProjName] = useState('');
  const [newProjDesc, setNewProjDesc] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const navItems = [
    { id: 'dashboard', label: 'Research Dashboard', icon: LayoutDashboard },
    { id: 'library', label: 'Paper Library', icon: BookOpen },
    { id: 'assistant', label: 'AI Research Assistant', icon: Bot, badge: 'RAG' },
    { id: 'comparison', label: 'Paper Comparison', icon: GitCompare },
    { id: 'gaps', label: 'Research Gap Analyzer', icon: Compass },
    { id: 'reviews', label: 'Literature Reviews', icon: FileText, badge: 'Export' },
  ];

  const handleCreateProject = async (e) => {
    e.preventDefault();
    if (!newProjName.trim()) return;
    setIsSubmitting(true);
    try {
      await createProject(newProjName, newProjDesc);
      setNewProjName('');
      setNewProjDesc('');
      setShowNewProject(false);
    } catch (err) {
      console.error(err);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleNavClick = (tabId) => {
    setActiveTab(tabId);
    if (onClose) onClose();
  };

  return (
    <>
      {/* Mobile Backdrop Overlay */}
      {isOpen && (
        <div 
          onClick={onClose}
          className="fixed inset-0 z-40 bg-slate-900/60 backdrop-blur-xs lg:hidden transition-opacity"
          aria-hidden="true"
        />
      )}

      {/* Sidebar / Drawer Container */}
      <aside 
        className={`fixed inset-y-0 left-0 z-50 w-72 lg:w-64 bg-white dark:bg-navy-900 border-r border-slate-200 dark:border-slate-800 flex flex-col h-full select-none transition-transform duration-200 ease-in-out lg:static lg:translate-x-0 ${
          isOpen ? 'translate-x-0 shadow-2xl' : '-translate-x-full lg:translate-x-0'
        }`}
      >
        {/* Brand Header */}
        <div className="p-4 sm:p-5 border-b border-slate-200 dark:border-slate-800 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-academic-700 via-academic-600 to-academic-500 flex items-center justify-center text-white shadow-md shadow-academic-500/20 shrink-0">
              <Sparkles className="w-5 h-5" />
            </div>
            <div>
              <h1 className="font-bold text-base tracking-tight text-slate-900 dark:text-white">
                ResearchMate AI
              </h1>
              <p className="text-[11px] text-slate-500 dark:text-slate-400 font-medium">Literature Review Assistant</p>
            </div>
          </div>
          {/* Close button on mobile */}
          <button
            onClick={onClose}
            className="p-1 rounded-lg text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-navy-800 lg:hidden"
            title="Close Menu"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Active Project Selector */}
        <div className="px-4 py-3 border-b border-slate-100 dark:border-slate-800/60 bg-slate-50/50 dark:bg-navy-950/40">
          <div className="flex items-center justify-between mb-1.5">
            <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-400 dark:text-slate-500 flex items-center gap-1">
              <Layers className="w-3 h-3" /> Research Project
            </span>
            <button 
              onClick={() => setShowNewProject(!showNewProject)}
              className="text-xs text-academic-600 dark:text-academic-400 hover:text-academic-700 font-medium flex items-center gap-0.5"
              title="Create Project"
            >
              <FolderPlus className="w-3.5 h-3.5" />
            </button>
          </div>

          {projects.length > 0 ? (
            <div className="relative">
              <select
                value={selectedProject ? selectedProject.id : ''}
                onChange={(e) => {
                  const proj = projects.find(p => p.id === parseInt(e.target.value));
                  if (proj) setSelectedProject(proj);
                }}
                className="w-full bg-white dark:bg-navy-850 border border-slate-200 dark:border-slate-700 text-slate-800 dark:text-slate-200 text-xs rounded-lg px-2.5 py-1.5 pr-8 truncate font-medium focus:outline-none focus:ring-1 focus:ring-academic-500"
              >
                {projects.map((p) => (
                  <option key={p.id} value={p.id}>
                    {p.name} ({p.paper_count || 0} papers)
                  </option>
                ))}
              </select>
            </div>
          ) : (
            <p className="text-xs text-slate-400 italic">No projects created yet</p>
          )}

          {/* Quick New Project Inline Form */}
          {showNewProject && (
            <form onSubmit={handleCreateProject} className="mt-2.5 p-2 bg-white dark:bg-navy-850 border border-academic-200 dark:border-academic-800 rounded-lg shadow-sm space-y-2">
              <input
                type="text"
                placeholder="Project Title..."
                value={newProjName}
                onChange={(e) => setNewProjName(e.target.value)}
                className="w-full text-xs px-2 py-1 rounded bg-slate-50 dark:bg-navy-900 border border-slate-200 dark:border-slate-700 text-slate-800 dark:text-slate-200 focus:outline-none"
                autoFocus
              />
              <div className="flex justify-end gap-1.5">
                <button
                  type="button"
                  onClick={() => setShowNewProject(false)}
                  className="text-[11px] px-2 py-0.5 rounded text-slate-500 hover:bg-slate-100 dark:hover:bg-navy-800"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isSubmitting || !newProjName.trim()}
                  className="text-[11px] px-2 py-0.5 rounded bg-academic-600 text-white font-medium hover:bg-academic-700 disabled:opacity-50"
                >
                  Save
                </button>
              </div>
            </form>
          )}
        </div>

        {/* Main Navigation */}
        <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => handleNavClick(item.id)}
                className={`w-full flex items-center justify-between px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-150 ${
                  isActive
                    ? 'bg-academic-50 text-academic-700 dark:bg-academic-950/70 dark:text-academic-300 font-semibold shadow-xs border border-academic-200/50 dark:border-academic-800/50'
                    : 'text-slate-600 dark:text-slate-400 hover:bg-slate-100/70 dark:hover:bg-navy-850 hover:text-slate-900 dark:hover:text-slate-200'
                }`}
              >
                <div className="flex items-center gap-3">
                  <Icon className={`w-4 h-4 ${isActive ? 'text-academic-600 dark:text-academic-400' : 'text-slate-400 dark:text-slate-500'}`} />
                  <span>{item.label}</span>
                </div>
                {item.badge && (
                  <span className={`text-[10px] font-bold px-1.5 py-0.5 rounded-full ${
                    isActive 
                      ? 'bg-academic-200 text-academic-800 dark:bg-academic-900 dark:text-academic-300' 
                      : 'bg-slate-100 text-slate-500 dark:bg-navy-800 dark:text-slate-400'
                  }`}>
                    {item.badge}
                  </span>
                )}
              </button>
            );
          })}
        </nav>

        {/* Footer / User Profile & Controls */}
        <div className="p-3 border-t border-slate-200 dark:border-slate-800 space-y-2">
          <div className="flex items-center justify-between px-2 py-1.5 rounded-lg bg-slate-50 dark:bg-navy-950">
            <div className="flex items-center gap-2 overflow-hidden">
              <div className="w-8 h-8 rounded-full bg-academic-600 text-white font-bold text-xs flex items-center justify-center shrink-0">
                {user?.full_name ? user.full_name[0].toUpperCase() : 'R'}
              </div>
              <div className="overflow-hidden">
                <p className="text-xs font-semibold text-slate-900 dark:text-slate-100 truncate">
                  {user?.full_name || 'Researcher'}
                </p>
                <p className="text-[10px] text-slate-500 dark:text-slate-400 truncate">
                  {user?.email || 'researcher@academic.edu'}
                </p>
              </div>
            </div>
            <button
              onClick={toggleTheme}
              className="p-1.5 text-slate-500 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white rounded-lg hover:bg-slate-200/50 dark:hover:bg-navy-850 transition-colors"
              title={isDark ? "Switch to Light Theme" : "Switch to Dark Theme"}
            >
              {isDark ? <Sun className="w-4 h-4 text-amber-400" /> : <Moon className="w-4 h-4" />}
            </button>
          </div>

          <button
            onClick={logout}
            className="w-full flex items-center gap-2 px-3 py-2 text-xs text-rose-600 dark:text-rose-400 hover:bg-rose-50 dark:hover:bg-rose-950/30 rounded-lg font-medium transition-colors"
          >
            <LogOut className="w-3.5 h-3.5" />
            <span>Sign Out</span>
          </button>
        </div>
      </aside>
    </>
  );
}
