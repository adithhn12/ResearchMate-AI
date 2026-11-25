import React, { useState } from 'react';
import { Sparkles, BookOpen, Bot, Compass, ArrowRight, Loader2, Lock, Mail, User } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';

export default function Auth() {
  const { login, register, demoLogin } = useAuth();
  const [isRegister, setIsRegister] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');

  const extractAuthError = (err, fallback) => {
    const status = err.response?.status;
    const detail = err.response?.data?.detail;
    if (typeof detail === 'string' && detail.trim()) {
      return detail;
    }
    if (Array.isArray(detail) && detail.length > 0) {
      return detail.map(d => d.msg || JSON.stringify(d)).join('; ');
    }
    if (status) {
      return `${fallback} (HTTP ${status})`;
    }
    if (err.message) {
      return `Unable to reach backend server (${err.message}).`;
    }
    return fallback;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErrorMsg('');
    setLoading(true);
    try {
      if (isRegister) {
        await register(email, password, fullName);
      } else {
        await login(email, password);
      }
    } catch (err) {
      console.error(err);
      setErrorMsg(extractAuthError(err, "Authentication failed."));
    } finally {
      setLoading(false);
    }
  };

  const handleDemoAccess = async () => {
    setErrorMsg('');
    setLoading(true);
    try {
      await demoLogin();
    } catch (err) {
      console.error(err);
      setErrorMsg(extractAuthError(err, "Demo login failed."));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex bg-slate-900 text-white selection:bg-academic-500">
      {/* Left Hero Panel */}
      <div className="hidden lg:flex flex-1 flex-col justify-between p-12 bg-gradient-to-br from-navy-950 via-slate-900 to-academic-950 border-r border-slate-800/60 relative overflow-hidden">
        <div className="space-y-6 relative z-10">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-academic-600 flex items-center justify-center shadow-lg shadow-academic-600/30">
              <Sparkles className="w-5 h-5 text-white" />
            </div>
            <h1 className="text-xl font-extrabold tracking-tight">
              ResearchMate <span className="text-academic-400">AI</span>
            </h1>
          </div>

          <div className="space-y-3 max-w-lg pt-8">
            <h2 className="text-3xl font-extrabold tracking-tight leading-tight">
              AI-Powered Literature Review & Academic Research Assistant
            </h2>
            <p className="text-sm text-slate-400 leading-relaxed">
              Upload multiple peer-reviewed papers, query with grounded RAG citations, perform methodology comparisons, discover research gaps, and generate structured literature reviews.
            </p>
          </div>

          <div className="space-y-4 pt-6">
            <div className="flex items-start gap-3 p-3.5 rounded-xl bg-white/5 border border-white/10 max-w-md">
              <Bot className="w-5 h-5 text-academic-400 mt-0.5 shrink-0" />
              <div className="text-xs space-y-0.5">
                <p className="font-semibold text-white">Traditional Multi-Doc RAG</p>
                <p className="text-slate-400">PyMuPDF text extraction, chunking, all-MiniLM-L6-v2 embeddings, ChromaDB, and Gemini with verified inline citations.</p>
              </div>
            </div>

            <div className="flex items-start gap-3 p-3.5 rounded-xl bg-white/5 border border-white/10 max-w-md">
              <Compass className="w-5 h-5 text-academic-400 mt-0.5 shrink-0" />
              <div className="text-xs space-y-0.5">
                <p className="font-semibold text-white">Research Gap & Limitation Analyzer</p>
                <p className="text-slate-400">Distinguishes author-stated limitations from AI-inferred unexplored opportunities.</p>
              </div>
            </div>

            <div className="flex items-start gap-3 p-3.5 rounded-xl bg-white/5 border border-white/10 max-w-md">
              <BookOpen className="w-5 h-5 text-academic-400 mt-0.5 shrink-0" />
              <div className="text-xs space-y-0.5">
                <p className="font-semibold text-white">Publication-Ready Reviews with DOCX/PDF Export</p>
                <p className="text-slate-400">8-section structured review synthesis with ReportLab and python-docx document generation.</p>
              </div>
            </div>
          </div>
        </div>

        <div className="text-xs text-slate-500 relative z-10">
          © 2026 ResearchMate AI • Academic Research Workspace
        </div>
      </div>

      {/* Right Login / Register Form */}
      <div className="flex-1 flex items-center justify-center p-8 bg-navy-950">
        <div className="w-full max-w-md space-y-6">
          <div className="space-y-2">
            <h3 className="text-2xl font-bold tracking-tight text-white">
              {isRegister ? 'Create Researcher Account' : 'Welcome Back'}
            </h3>
            <p className="text-xs text-slate-400">
              {isRegister ? 'Sign up to begin indexing and reviewing academic papers.' : 'Sign in to access your literature review workspaces.'}
            </p>
          </div>

          {/* Quick Demo Access Button */}
          <button
            onClick={handleDemoAccess}
            disabled={loading}
            className="w-full py-2.5 px-4 rounded-xl bg-gradient-to-r from-academic-600 to-indigo-600 hover:from-academic-500 hover:to-indigo-500 text-white font-semibold text-xs flex items-center justify-center gap-2 shadow-md transition-all"
          >
            <Sparkles className="w-4 h-4 text-amber-300" />
            <span>Instant One-Click Demo Access</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>

          <div className="relative flex items-center justify-center">
            <div className="border-t border-slate-800 w-full" />
            <span className="bg-navy-950 px-3 text-[11px] text-slate-500 uppercase tracking-wider shrink-0">
              Or sign in with email
            </span>
            <div className="border-t border-slate-800 w-full" />
          </div>

          {errorMsg && (
            <div className="p-3 rounded-lg bg-rose-950/50 border border-rose-800 text-xs text-rose-300">
              {errorMsg}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            {isRegister && (
              <div className="space-y-1">
                <label className="text-xs font-semibold text-slate-300">Full Name / Academic Title</label>
                <div className="relative">
                  <User className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
                  <input
                    type="text"
                    required
                    placeholder="Dr. Alex Rivera"
                    value={fullName}
                    onChange={(e) => setFullName(e.target.value)}
                    className="w-full pl-9 pr-4 py-2.5 bg-slate-900 border border-slate-800 rounded-xl text-xs text-white placeholder-slate-500 focus:outline-none focus:ring-1 focus:ring-academic-500"
                  />
                </div>
              </div>
            )}

            <div className="space-y-1">
              <label className="text-xs font-semibold text-slate-300">Email Address</label>
              <div className="relative">
                <Mail className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
                <input
                  type="email"
                  required
                  placeholder="researcher@university.edu"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full pl-9 pr-4 py-2.5 bg-slate-900 border border-slate-800 rounded-xl text-xs text-white placeholder-slate-500 focus:outline-none focus:ring-1 focus:ring-academic-500"
                />
              </div>
            </div>

            <div className="space-y-1">
              <label className="text-xs font-semibold text-slate-300">Password</label>
              <div className="relative">
                <Lock className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
                <input
                  type="password"
                  required
                  placeholder="••••••••"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full pl-9 pr-4 py-2.5 bg-slate-900 border border-slate-800 rounded-xl text-xs text-white placeholder-slate-500 focus:outline-none focus:ring-1 focus:ring-academic-500"
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full py-2.5 px-4 rounded-xl bg-academic-600 hover:bg-academic-700 text-white font-semibold text-xs flex items-center justify-center gap-2 transition-all disabled:opacity-50"
            >
              {loading ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <span>{isRegister ? 'Register & Initialize Workspace' : 'Sign In'}</span>
              )}
            </button>
          </form>

          <div className="text-center">
            <button
              type="button"
              onClick={() => {
                setIsRegister(!isRegister);
                setErrorMsg('');
              }}
              className="text-xs text-academic-400 hover:underline font-medium"
            >
              {isRegister ? 'Already have an account? Sign in' : "Don't have an account? Create one"}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
