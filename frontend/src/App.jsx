import React from 'react';
import ChatWidget from './components/ChatWidget';

function App() {
  return (
    <div className="min-h-screen bg-zinc-100 dark:bg-zinc-900 text-zinc-900 dark:text-zinc-100 p-8 flex flex-col items-center justify-center">
      <div className="max-w-2xl text-center space-y-6">
        <h1 className="text-4xl md:text-6xl font-bold bg-gradient-to-r from-emerald-500 to-cyan-500 bg-clip-text text-transparent">
          Manoj's Portfolio
        </h1>
        <p className="text-xl text-zinc-600 dark:text-zinc-400">
          This is a demo page. Click the icon in the bottom right to chat with the AI Assistant!
        </p>

        <div className="p-6 bg-white dark:bg-black/20 rounded-2xl border border-zinc-200 dark:border-zinc-800 shadow-sm">
          <h2 className="text-lg font-semibold mb-2">Instructions</h2>
          <ol className="text-left list-decimal list-inside space-y-2 text-zinc-600 dark:text-zinc-400">
            <li>Ensure the backend is running on port 8000.</li>
            <li>Make sure you have added your Google API Key in <code className="bg-zinc-200 dark:bg-zinc-800 px-1 rounded">backend/.env</code>.</li>
            <li>Click the chat bubble.</li>
            <li>Ask questions like "What is this RAG-Bot project?"</li>
          </ol>
        </div>
      </div>

      <ChatWidget />
    </div>
  );
}

export default App;
