import React, { useState } from 'react';
import { ThemeProvider } from './contexts/ThemeContext';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import { ProjectProvider, useProject } from './contexts/ProjectContext';
import Sidebar from './components/Sidebar';
import Navbar from './components/Navbar';
import UploadModal from './components/UploadModal';
import Dashboard from './pages/Dashboard';
import Library from './pages/Library';
import Assistant from './pages/Assistant';
import Comparison from './pages/Comparison';
import Auth from './pages/Auth';
import { Loader2 } from 'lucide-react';

function MainApp() {
  const { isAuthenticated, loading } = useAuth();
  const { fetchProjects } = useProject();
  const [activeTab, setActiveTab] = useState('dashboard');
  const [isUploadOpen, setIsUploadOpen] = useState(false);
  const [isMobileSidebarOpen, setIsMobileSidebarOpen] = useState(false);

  if (loading) {
    return (
      <div className="min-h-screen bg-navy-950 flex flex-col items-center justify-center gap-3 text-white">
        <Loader2 className="w-8 h-8 text-academic-500 animate-spin" />
        <p className="text-xs text-slate-400">Loading ResearchMate AI workspace...</p>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Auth />;
  }

  const renderActiveTab = () => {
    switch (activeTab) {
      case 'dashboard':
        return <Dashboard setActiveTab={setActiveTab} onOpenUpload={() => setIsUploadOpen(true)} />;
      case 'library':
        return <Library onOpenUpload={() => setIsUploadOpen(true)} />;
      case 'assistant':
        return <Assistant />;
      case 'comparison':
        return <Comparison />;
      default:
        return <Dashboard setActiveTab={setActiveTab} onOpenUpload={() => setIsUploadOpen(true)} />;
    }
  };

  return (
    <div className="flex h-screen bg-slate-50 dark:bg-navy-950 overflow-hidden font-sans">
      <Sidebar 
        activeTab={activeTab} 
        setActiveTab={setActiveTab} 
        isOpen={isMobileSidebarOpen}
        onClose={() => setIsMobileSidebarOpen(false)}
      />
      
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        <Navbar 
          activeTab={activeTab} 
          setActiveTab={setActiveTab} 
          onOpenUpload={() => setIsUploadOpen(true)} 
          onToggleSidebar={() => setIsMobileSidebarOpen(prev => !prev)}
        />
        <main className="flex-1 overflow-y-auto">
          {renderActiveTab()}
        </main>
      </div>

      <UploadModal 
        isOpen={isUploadOpen} 
        onClose={() => setIsUploadOpen(false)}
        onUploadSuccess={() => {
          fetchProjects();
        }}
      />
    </div>
  );
}

export default function App() {
  return (
    <ThemeProvider>
      <AuthProvider>
        <ProjectProvider>
          <MainApp />
        </ProjectProvider>
      </AuthProvider>
    </ThemeProvider>
  );
}
