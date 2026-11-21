import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

export default function MarkdownRenderer({ content, className = '' }) {
  if (!content) return null;

  return (
    <div className={`academic-markdown prose dark:prose-invert max-w-none text-xs sm:text-sm leading-relaxed ${className}`}>
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
          h1: ({ node, ...props }) => (
            <h1 className="text-base sm:text-lg font-bold text-slate-900 dark:text-white mt-4 mb-2 pb-1 border-b border-slate-200 dark:border-slate-800" {...props} />
          ),
          h2: ({ node, ...props }) => (
            <h2 className="text-sm sm:text-base font-bold text-slate-900 dark:text-white mt-3.5 mb-1.5" {...props} />
          ),
          h3: ({ node, ...props }) => (
            <h3 className="text-xs sm:text-sm font-bold text-academic-700 dark:text-academic-400 mt-2.5 mb-1" {...props} />
          ),
          h4: ({ node, ...props }) => (
            <h4 className="text-xs font-bold text-slate-800 dark:text-slate-200 mt-2 mb-1" {...props} />
          ),
          p: ({ node, ...props }) => (
            <p className="mb-2.5 last:mb-0 text-slate-700 dark:text-slate-300 leading-relaxed" {...props} />
          ),
          strong: ({ node, ...props }) => (
            <strong className="font-semibold text-slate-900 dark:text-white" {...props} />
          ),
          em: ({ node, ...props }) => (
            <em className="italic text-slate-800 dark:text-slate-200" {...props} />
          ),
          ul: ({ node, ...props }) => (
            <ul className="list-disc pl-5 mb-3 space-y-1 text-slate-700 dark:text-slate-300" {...props} />
          ),
          ol: ({ node, ...props }) => (
            <ol className="list-decimal pl-5 mb-3 space-y-1 text-slate-700 dark:text-slate-300" {...props} />
          ),
          li: ({ node, ...props }) => (
            <li className="leading-relaxed pl-0.5" {...props} />
          ),
          blockquote: ({ node, ...props }) => (
            <blockquote className="border-l-4 border-academic-500 pl-3.5 py-1 my-3 bg-academic-50/50 dark:bg-academic-950/30 text-slate-700 dark:text-slate-300 italic rounded-r" {...props} />
          ),
          code: ({ node, inline, className, children, ...props }) => {
            if (inline) {
              return (
                <code className="px-1.5 py-0.5 rounded bg-slate-100 dark:bg-navy-800 text-academic-600 dark:text-academic-400 font-mono text-[11px] font-medium" {...props}>
                  {children}
                </code>
              );
            }
            return (
              <div className="overflow-x-auto my-3 rounded-lg border border-slate-200 dark:border-slate-800 bg-slate-900 text-slate-100 p-3">
                <code className="font-mono text-xs block leading-relaxed" {...props}>
                  {children}
                </code>
              </div>
            );
          },
          table: ({ node, ...props }) => (
            <div className="overflow-x-auto my-4 rounded-lg border border-slate-200 dark:border-slate-800">
              <table className="w-full text-xs text-left border-collapse" {...props} />
            </div>
          ),
          thead: ({ node, ...props }) => (
            <thead className="bg-slate-50 dark:bg-navy-950 border-b border-slate-200 dark:border-slate-800" {...props} />
          ),
          th: ({ node, ...props }) => (
            <th className="p-2.5 font-bold text-slate-800 dark:text-slate-200 whitespace-nowrap" {...props} />
          ),
          td: ({ node, ...props }) => (
            <td className="p-2.5 border-t border-slate-100 dark:border-slate-800 text-slate-700 dark:text-slate-300" {...props} />
          ),
          a: ({ node, ...props }) => (
            <a 
              className="text-academic-600 dark:text-academic-400 underline hover:text-academic-700 font-medium" 
              target="_blank" 
              rel="noopener noreferrer" 
              {...props} 
            />
          ),
          hr: ({ node, ...props }) => (
            <hr className="my-4 border-slate-200 dark:border-slate-800" {...props} />
          ),
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  );
}
