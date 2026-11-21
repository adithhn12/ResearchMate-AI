import React, { useState, useEffect, useRef } from 'react';
import { 
  Bot, 
  Send, 
  Plus, 
  Trash2, 
  BookOpen, 
  Sparkles, 
  Layers, 
  Loader2, 
  ChevronRight, 
  Quote, 
  Check, 
  ExternalLink,
  MessageSquare,
  SlidersHorizontal,
  X,
  FileCheck2
} from 'lucide-react';
import { chatApi, papersApi } from '../api/client';
import { useProject } from '../contexts/ProjectContext';
import MarkdownRenderer from '../components/MarkdownRenderer';

export default function Assistant() {
  const { selectedProject } = useProject();
  const [sessions, setSessions] = useState([]);
  const [activeSession, setActiveSession] = useState(null);
  const [messages, setMessages] = useState([]);
  const [papers, setPapers] = useState([]);
  const [selectedPaperIds, setSelectedPaperIds] = useState([]);
  const [inputQuestion, setInputQuestion] = useState('');
  const [isSending, setIsSending] = useState(false);
  const [activeSourceSnippet, setActiveSourceSnippet] = useState(null);
  const [showMobilePanel, setShowMobilePanel] = useState(false);
  const messagesEndRef = useRef(null);

  // Fetch papers in project for paper selector filter
  useEffect(() => {
    if (!selectedProject) return;
    const loadPapers = async () => {
      try {
        const res = await papersApi.listByProject(selectedProject.id);
        setPapers(res.data);
        // By default, select all successfully indexed papers
        const indexedIds = res.data.filter(p => p.status === 'indexed').map(p => p.id);
        setSelectedPaperIds(indexedIds);
      } catch (err) {
        console.error("Error loading papers for assistant:", err);
      }
    };
    loadPapers();
  }, [selectedProject]);

  // Fetch chat sessions
  const loadSessions = async () => {
    if (!selectedProject) return;
    try {
      const res = await chatApi.getSessions(selectedProject.id);
      setSessions(res.data);
      if (res.data.length > 0 && !activeSession) {
        selectSession(res.data[0]);
      }
    } catch (err) {
      console.error("Error loading chat sessions:", err);
    }
  };

  useEffect(() => {
    loadSessions();
  }, [selectedProject]);

  // Load messages for chosen session
  const selectSession = async (session) => {
    setActiveSession(session);
    setShowMobilePanel(false);
    try {
      const res = await chatApi.getMessages(session.id);
      setMessages(res.data);
    } catch (err) {
      console.error("Error loading messages:", err);
    }
  };

  const handleNewSession = async () => {
    if (!selectedProject) return;
    try {
      const res = await chatApi.createSession(selectedProject.id, "New Research Discussion");
      setSessions(prev => [res.data, ...prev]);
      setActiveSession(res.data);
      setMessages([]);
      setShowMobilePanel(false);
    } catch (err) {
      console.error("Error creating session:", err);
    }
  };

  const handleDeleteSession = async (sessionId, e) => {
    e.stopPropagation();
    try {
      await chatApi.deleteSession(sessionId);
      setSessions(prev => prev.filter(s => s.id !== sessionId));
      if (activeSession?.id === sessionId) {
        setActiveSession(null);
        setMessages([]);
      }
    } catch (err) {
      console.error("Error deleting session:", err);
    }
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isSending]);

  const handleSendMessage = async (e) => {
    e?.preventDefault();
    if (!inputQuestion.trim() || isSending) return;

    const questionText = inputQuestion.trim();
    setInputQuestion('');

    // Optimistically add user message
    const tempUserMsg = {
      id: Date.now(),
      role: 'user',
      content: questionText,
      sources: [],
      created_at: new Date().toISOString()
    };
    setMessages(prev => [...prev, tempUserMsg]);
    setIsSending(true);

    try {
      const res = await chatApi.sendMessage(
        questionText,
        activeSession?.id,
        selectedPaperIds
      );
      setMessages(prev => [...prev, res.data]);
      loadSessions();
    } catch (err) {
      console.error("Error sending message:", err);
      setMessages(prev => [
        ...prev,
        {
          id: Date.now() + 1,
          role: 'assistant',
          content: '⚠️ Failed to get AI response. Please check your network and Gemini API configuration.',
          sources: []
        }
      ]);
    } finally {
      setIsSending(false);
    }
  };

  const togglePaperSelection = (id) => {
    setSelectedPaperIds(prev => 
      prev.includes(id) ? prev.filter(pId => pId !== id) : [...prev, id]
    );
  };

  const indexedPapers = papers.filter(p => p.status === 'indexed');
  const allIndexedSelected = indexedPapers.length > 0 && indexedPapers.every(p => selectedPaperIds.includes(p.id));

  const handleResetToAll = () => {
    if (allIndexedSelected) {
      setSelectedPaperIds([]);
    } else {
      setSelectedPaperIds(indexedPapers.map(p => p.id));
    }
  };

  const suggestedPrompts = [
    "Compare the research objectives and methodologies across the selected papers.",
    "Summarize the key empirical results and benchmark findings.",
    "What algorithms and embedding models were evaluated?",
    "What explicit constraints and limitations did the authors encounter?"
  ];

  return (
    <div className="flex h-[calc(100vh-4rem)] overflow-hidden relative">
      {/* Mobile Thread/Scope Panel Backdrop */}
      {showMobilePanel && (
        <div 
          onClick={() => setShowMobilePanel(false)}
          className="fixed inset-0 z-30 bg-slate-900/60 backdrop-blur-xs lg:hidden"
        />
      )}

      {/* Left Chat Sessions & Paper Selection Drawer/Sidebar */}
      <div className={`fixed lg:static inset-y-0 left-0 z-40 w-80 lg:w-72 bg-white dark:bg-navy-900 border-r border-slate-200 dark:border-slate-800 flex flex-col shrink-0 transition-transform duration-200 ease-in-out ${
        showMobilePanel ? 'translate-x-0 shadow-2xl' : '-translate-x-full lg:translate-x-0'
      }`}>
        <div className="p-4 border-b border-slate-200 dark:border-slate-800 flex items-center justify-between">
          <span className="text-xs font-bold uppercase tracking-wider text-slate-500">
            Chat Threads
          </span>
          <div className="flex items-center gap-1.5">
            <button
              onClick={handleNewSession}
              className="p-1.5 rounded-lg bg-academic-50 dark:bg-navy-850 hover:bg-academic-100 text-academic-600 dark:text-academic-400 font-semibold text-xs flex items-center gap-1 transition-colors"
              title="Start New Thread"
            >
              <Plus className="w-3.5 h-3.5" /> New
            </button>
            <button
              onClick={() => setShowMobilePanel(false)}
              className="p-1 rounded-lg text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 lg:hidden"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Paper Filter Bar (Multi-Document Selection) */}
        {papers.length > 0 && (
          <div className="p-3 border-b border-slate-100 dark:border-slate-800 bg-slate-50/60 dark:bg-navy-950/40">
            <div className="flex items-center justify-between text-[11px] font-semibold text-slate-500 mb-1.5">
              <span className="flex items-center gap-1">
                <FileCheck2 className="w-3 h-3 text-academic-500" />
                Query Scope ({selectedPaperIds.length}/{indexedPapers.length})
              </span>
              <button
                onClick={handleResetToAll}
                className="text-academic-600 dark:text-academic-400 hover:underline font-medium text-[11px]"
              >
                {allIndexedSelected ? 'Deselect All' : 'Reset to All'}
              </button>
            </div>
            <div className="max-h-32 overflow-y-auto space-y-1 pr-1">
              {papers.map(p => {
                const isSelected = selectedPaperIds.includes(p.id);
                const isIndexed = p.status === 'indexed';
                return (
                  <button
                    key={p.id}
                    onClick={() => isIndexed && togglePaperSelection(p.id)}
                    disabled={!isIndexed}
                    className={`w-full text-left text-[11px] px-2 py-1.5 rounded-lg truncate flex items-center justify-between gap-1.5 transition-colors ${
                      isSelected 
                        ? 'bg-academic-600 text-white font-medium shadow-xs'
                        : isIndexed
                        ? 'text-slate-700 dark:text-slate-300 hover:bg-slate-200/50 dark:hover:bg-navy-800'
                        : 'text-slate-400 opacity-60 cursor-not-allowed'
                    }`}
                  >
                    <div className="flex items-center gap-1.5 truncate">
                      <BookOpen className="w-3 h-3 shrink-0" />
                      <span className="truncate">{p.title}</span>
                    </div>
                    {isSelected && <Check className="w-3 h-3 shrink-0" />}
                  </button>
                );
              })}
            </div>
          </div>
        )}

        {/* Sessions List */}
        <div className="flex-1 overflow-y-auto p-2 space-y-1">
          {sessions.map((s) => {
            const isActive = activeSession?.id === s.id;
            return (
              <div
                key={s.id}
                onClick={() => selectSession(s)}
                className={`group flex items-center justify-between px-3 py-2.5 rounded-lg cursor-pointer text-xs transition-colors ${
                  isActive
                    ? 'bg-academic-50 text-academic-700 dark:bg-navy-800 dark:text-academic-300 font-semibold border border-academic-200/60 dark:border-academic-800/60'
                    : 'text-slate-600 dark:text-slate-400 hover:bg-slate-100/60 dark:hover:bg-navy-850 hover:text-slate-900 dark:hover:text-slate-200'
                }`}
              >
                <div className="flex items-center gap-2 truncate">
                  <MessageSquare className="w-3.5 h-3.5 shrink-0 text-slate-400" />
                  <span className="truncate">{s.title}</span>
                </div>
                <button
                  onClick={(e) => handleDeleteSession(s.id, e)}
                  className="opacity-0 group-hover:opacity-100 p-1 hover:text-rose-500 transition-opacity"
                  title="Delete Thread"
                >
                  <Trash2 className="w-3.5 h-3.5" />
                </button>
              </div>
            );
          })}

          {sessions.length === 0 && (
            <div className="p-4 text-center text-xs text-slate-400">
              No conversations yet. Ask your first research question!
            </div>
          )}
        </div>
      </div>

      {/* Main Chat Conversation Stream */}
      <div className="flex-1 flex flex-col bg-slate-50 dark:bg-navy-950 overflow-hidden min-w-0">
        {/* Mobile Scope & Thread Bar */}
        <div className="lg:hidden px-4 py-2 bg-white dark:bg-navy-900 border-b border-slate-200 dark:border-slate-800 flex items-center justify-between text-xs shrink-0">
          <button
            onClick={() => setShowMobilePanel(true)}
            className="flex items-center gap-1.5 text-academic-600 dark:text-academic-400 font-medium py-1 px-2 rounded-md hover:bg-slate-100 dark:hover:bg-navy-850"
          >
            <SlidersHorizontal className="w-3.5 h-3.5" />
            <span>Threads & Scope ({selectedPaperIds.length} papers)</span>
          </button>
          <span className="text-[11px] text-slate-400 truncate max-w-[150px]">
            {activeSession ? activeSession.title : 'New Discussion'}
          </span>
        </div>

        {/* Messages Scroll Area */}
        <div className="flex-1 overflow-y-auto p-4 sm:p-6 space-y-6">
          {messages.length === 0 ? (
            <div className="max-w-xl mx-auto my-8 sm:my-12 text-center space-y-6 px-2">
              <div className="w-14 h-14 rounded-2xl bg-academic-100 dark:bg-navy-850 text-academic-600 dark:text-academic-400 flex items-center justify-center mx-auto shadow-xs">
                <Bot className="w-7 h-7" />
              </div>
              <div className="space-y-2">
                <h3 className="font-bold text-base sm:text-lg text-slate-900 dark:text-white">
                  Multi-Document Academic RAG Assistant
                </h3>
                <p className="text-xs text-slate-500 leading-relaxed max-w-md mx-auto">
                  Ask grounded questions across your selected peer-reviewed papers. Answers are retrieved via vector similarity search with source diversity and synthesized with accurate citations.
                </p>
                {selectedPaperIds.length > 0 && (
                  <p className="text-[11px] text-academic-600 dark:text-academic-400 font-medium">
                    Currently querying {selectedPaperIds.length} selected paper{selectedPaperIds.length > 1 ? 's' : ''} in this project.
                  </p>
                )}
              </div>

              {/* Sample Prompts */}
              <div className="space-y-2 pt-2">
                <p className="text-[11px] font-bold uppercase tracking-wider text-slate-400">
                  Recommended Inquiries
                </p>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-left">
                  {suggestedPrompts.map((prompt, i) => (
                    <button
                      key={i}
                      onClick={() => setInputQuestion(prompt)}
                      className="p-3 bg-white dark:bg-navy-900 border border-slate-200 dark:border-slate-800 hover:border-academic-400 dark:hover:border-academic-600 rounded-xl text-xs text-slate-700 dark:text-slate-300 transition-all text-left shadow-xs"
                    >
                      "{prompt}"
                    </button>
                  ))}
                </div>
              </div>
            </div>
          ) : (
            <div className="max-w-3xl mx-auto space-y-5">
              {messages.map((msg, idx) => {
                const isAssistant = msg.role === 'assistant';
                return (
                  <div
                    key={msg.id || idx}
                    className={`flex gap-2.5 sm:gap-3.5 ${isAssistant ? 'items-start' : 'items-start flex-row-reverse'}`}
                  >
                    {/* Avatar */}
                    <div className={`w-7 h-7 sm:w-8 sm:h-8 rounded-lg flex items-center justify-center text-xs font-bold shrink-0 ${
                      isAssistant
                        ? 'bg-academic-600 text-white shadow-xs'
                        : 'bg-slate-700 text-white'
                    }`}>
                      {isAssistant ? <Bot className="w-4 h-4" /> : 'You'}
                    </div>

                    {/* Message Bubble */}
                    <div className={`space-y-3 max-w-[92%] sm:max-w-[85%] ${
                      isAssistant
                        ? 'bg-white dark:bg-navy-900 border border-slate-200 dark:border-slate-800 p-4 sm:p-5 rounded-2xl shadow-xs text-slate-800 dark:text-slate-100 overflow-hidden'
                        : 'bg-academic-600 text-white p-3.5 sm:p-4 rounded-2xl shadow-xs text-xs sm:text-sm'
                    }`}>
                      {/* Markdown Rendered Content */}
                      {isAssistant ? (
                        <MarkdownRenderer content={msg.content} />
                      ) : (
                        <div className="whitespace-pre-wrap leading-relaxed">
                          {msg.content}
                        </div>
                      )}

                      {/* Grounded Source Citations */}
                      {isAssistant && msg.sources && msg.sources.length > 0 && (
                        <div className="pt-3 border-t border-slate-100 dark:border-slate-800/80 space-y-2">
                          <span className="text-[11px] font-bold uppercase tracking-wider text-academic-600 dark:text-academic-400 flex items-center gap-1">
                            <Quote className="w-3 h-3" /> Grounded Academic Sources ({msg.sources.length})
                          </span>
                          <div className="flex flex-wrap gap-1.5">
                            {msg.sources.map((src, sIdx) => (
                              <button
                                key={sIdx}
                                onClick={() => setActiveSourceSnippet(src)}
                                className="inline-flex items-center gap-1.5 text-[11px] px-2.5 py-1 rounded-md bg-slate-100 dark:bg-navy-850 hover:bg-academic-50 dark:hover:bg-academic-950 text-slate-700 dark:text-slate-300 border border-slate-200 dark:border-slate-700 transition-colors"
                              >
                                <BookOpen className="w-3 h-3 text-academic-500 shrink-0" />
                                <span className="font-medium truncate max-w-[140px] sm:max-w-[200px]">{src.paper_title}</span>
                                <span className="text-academic-600 dark:text-academic-400 font-bold shrink-0">p. {src.page_number}</span>
                              </button>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                );
              })}

              {isSending && (
                <div className="flex gap-2.5 sm:gap-3.5 items-start">
                  <div className="w-7 h-7 sm:w-8 sm:h-8 rounded-lg bg-academic-600 text-white flex items-center justify-center shrink-0 shadow-xs">
                    <Bot className="w-4 h-4" />
                  </div>
                  <div className="bg-white dark:bg-navy-900 border border-slate-200 dark:border-slate-800 p-4 rounded-2xl shadow-xs flex items-center gap-2 text-xs text-slate-500">
                    <Loader2 className="w-4 h-4 text-academic-600 animate-spin shrink-0" />
                    <span>Retrieving diverse paper chunks and synthesizing grounded answer...</span>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>
          )}
        </div>

        {/* Sticky Input Bar at Bottom */}
        <div className="p-3 sm:p-4 bg-white dark:bg-navy-900 border-t border-slate-200 dark:border-slate-800 shrink-0">
          <form onSubmit={handleSendMessage} className="max-w-3xl mx-auto flex gap-2">
            <input
              type="text"
              placeholder={`Ask a question across ${selectedPaperIds.length > 0 ? selectedPaperIds.length : 'all'} papers...`}
              value={inputQuestion}
              onChange={(e) => setInputQuestion(e.target.value)}
              disabled={isSending}
              className="flex-1 px-3.5 sm:px-4 py-2.5 bg-slate-50 dark:bg-navy-950 border border-slate-200 dark:border-slate-800 rounded-xl text-xs sm:text-sm text-slate-900 dark:text-white placeholder-slate-400 focus:outline-none focus:ring-1 focus:ring-academic-500"
            />
            <button
              type="submit"
              disabled={!inputQuestion.trim() || isSending}
              className="academic-button-primary px-4 sm:px-5 py-2.5 text-xs shrink-0"
            >
              {isSending ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <>
                  <span className="hidden sm:inline">Send</span>
                  <Send className="w-3.5 h-3.5" />
                </>
              )}
            </button>
          </form>
        </div>
      </div>

      {/* Snippet Inspection Drawer / Bottom Modal on Mobile */}
      {activeSourceSnippet && (
        <>
          <div 
            onClick={() => setActiveSourceSnippet(null)}
            className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-xs lg:hidden"
          />
          <div className="fixed inset-y-0 right-0 z-50 w-full sm:w-96 bg-white dark:bg-navy-900 shadow-2xl border-l border-slate-200 dark:border-slate-800 p-5 sm:p-6 flex flex-col justify-between animate-in slide-in-from-right duration-200">
            <div className="space-y-4">
              <div className="flex items-center justify-between border-b border-slate-100 dark:border-slate-800 pb-3">
                <span className="text-xs font-bold uppercase tracking-wider text-academic-600 dark:text-academic-400 flex items-center gap-1.5">
                  <Quote className="w-4 h-4" /> Citation Verification
                </span>
                <button
                  onClick={() => setActiveSourceSnippet(null)}
                  className="p-1 rounded-md text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-navy-800"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>

              <div className="space-y-1">
                <h4 className="font-bold text-sm text-slate-900 dark:text-white leading-snug">
                  {activeSourceSnippet.paper_title}
                </h4>
                <p className="text-xs text-academic-600 dark:text-academic-400 font-semibold">
                  Page Reference: Page {activeSourceSnippet.page_number}
                </p>
              </div>

              <div className="bg-slate-50 dark:bg-navy-950 p-4 rounded-xl border border-slate-200 dark:border-slate-800 text-xs text-slate-700 dark:text-slate-300 leading-relaxed font-mono whitespace-pre-wrap max-h-[60vh] overflow-y-auto">
                "{activeSourceSnippet.snippet}"
              </div>
            </div>

            <button
              onClick={() => setActiveSourceSnippet(null)}
              className="academic-button-secondary text-xs w-full justify-center mt-4"
            >
              Close Citation
            </button>
          </div>
        </>
      )}
    </div>
  );
}
