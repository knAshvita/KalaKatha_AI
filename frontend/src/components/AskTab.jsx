import React, { useState } from 'react';
import { Send, Bot, User, Loader2, Sparkles, BookOpen, AlertCircle } from 'lucide-react';
import { askQuestion } from '../api/kalakathaApi';

const SUGGESTIONS = [
    "What can I learn from this artwork?",
    "Explain the symbolism of the key details and colors.",
    "What artistic technique is being used here?",
    "Tell me about the historical and cultural context.",
    "What are the most important things to notice?"
];

export default function AskTab({ sessionId, artworkTitle = "this artwork" }) {
    const [messages, setMessages] = useState([
        {
            sender: 'guide',
            text: `Welcome to the gallery. I am your KalaKatha AI docent for ${artworkTitle}. Ask me anything about its brushcraft, composition, symbolism, or art-historical background.`,
            sourceContext: []
        }
    ]);
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);
    const [errorMsg, setErrorMsg] = useState(null);

    const handleSend = async (queryText) => {
        const question = queryText || input;
        if (!question.trim() || loading) return;

        const userMessage = { sender: 'user', text: question };
        setMessages((prev) => [...prev, userMessage]);
        setInput('');
        setLoading(true);
        setErrorMsg(null);

        try {
            if (!sessionId) {
                throw new Error("No active session found. Please analyze an artwork first.");
            }

            const response = await askQuestion(sessionId, question);
            const guideMessage = {
                sender: 'guide',
                text: response.answer || 'Thank you for your question.',
                sourceContext: response.source_context || []
            };
            setMessages((prev) => [...prev, guideMessage]);
        } catch (err) {
            setErrorMsg(err.message || 'The docent could not answer right now.');
            setMessages((prev) => [
                ...prev,
                { sender: 'guide', text: `I apologize, but I could not retrieve an answer right now: ${err.message}`, isError: true }
            ]);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="space-y-4 flex flex-col h-[560px] rounded-3xl border border-stone-200/90 dark:border-stone-800 bg-white dark:bg-stone-900 p-5 shadow-sm animate-fade-in">
            {/* Header / Suggestions Ribbon */}
            <div className="space-y-2 border-b border-stone-100 dark:border-stone-800 pb-3">
                <div className="flex items-center justify-between">
                    <span className="text-[10px] uppercase tracking-widest font-bold text-amber-700 dark:text-amber-400 flex items-center gap-1.5">
                        <Sparkles className="w-3.5 h-3.5 text-amber-600" />
                        <span>Conversational Ask Agent</span>
                    </span>
                    <span className="text-[11px] text-stone-400">Grounded in Stored Artwork Analysis</span>
                </div>

                <div className="flex gap-2 overflow-x-auto pb-1 no-scrollbar">
                    {SUGGESTIONS.map((s, i) => (
                        <button
                            key={i}
                            type="button"
                            onClick={() => handleSend(s)}
                            className="text-[11px] whitespace-nowrap px-3.5 py-1.5 rounded-full bg-stone-100 dark:bg-stone-800 text-stone-700 dark:text-stone-300 hover:border-amber-600 dark:hover:border-amber-500 border border-transparent transition cursor-pointer active:scale-95"
                        >
                            {s}
                        </button>
                    ))}
                </div>
            </div>

            {/* Chat Messages Feed */}
            <div className="flex-1 overflow-y-auto space-y-4 pr-1.5 scrollbar-thin">
                {messages.map((m, idx) => (
                    <div
                        key={idx}
                        className={`flex gap-3 ${m.sender === 'user' ? 'justify-end' : 'justify-start'} animate-fade-in`}
                    >
                        {m.sender === 'guide' && (
                            <div className="w-8 h-8 rounded-full bg-amber-600 text-white flex items-center justify-center flex-shrink-0 mt-0.5 shadow-sm">
                                <Bot className="w-4 h-4" />
                            </div>
                        )}
                        <div className="max-w-[85%] space-y-1.5">
                            <div
                                className={`rounded-2xl px-4 py-3 text-xs md:text-sm leading-relaxed ${
                                    m.sender === 'user'
                                        ? 'bg-amber-600 text-white shadow-md rounded-br-xs'
                                        : m.isError
                                        ? 'bg-rose-50 dark:bg-rose-950/40 text-rose-800 dark:text-rose-200 border border-rose-200 dark:border-rose-900 rounded-bl-xs'
                                        : 'bg-stone-100 dark:bg-stone-800/90 text-stone-800 dark:text-stone-100 rounded-bl-xs shadow-2xs font-serif'
                                }`}
                            >
                                {m.text}
                            </div>

                            {/* Source Context Badges */}
                            {m.sourceContext && m.sourceContext.length > 0 && (
                                <div className="flex flex-wrap gap-1 px-1">
                                    <span className="text-[10px] text-stone-400 font-sans">Grounded in:</span>
                                    {m.sourceContext.map((src, sIdx) => (
                                        <span
                                            key={sIdx}
                                            className="text-[9px] uppercase tracking-wider px-1.5 py-0.5 rounded bg-amber-100 dark:bg-amber-950/80 text-amber-800 dark:text-amber-300 font-semibold"
                                        >
                                            {src}
                                        </span>
                                    ))}
                                </div>
                            )}
                        </div>
                        {m.sender === 'user' && (
                            <div className="w-8 h-8 rounded-full bg-stone-300 dark:bg-stone-700 text-stone-800 dark:text-stone-200 flex items-center justify-center flex-shrink-0 mt-0.5">
                                <User className="w-4 h-4" />
                            </div>
                        )}
                    </div>
                ))}

                {loading && (
                    <div className="flex items-center gap-2.5 text-xs text-stone-500 dark:text-stone-400 py-2">
                        <Loader2 className="w-4 h-4 animate-spin text-amber-600" />
                        <span>AskAgent is formulating an answer from artwork analysis...</span>
                    </div>
                )}
            </div>

            {/* Input Bar */}
            <form
                onSubmit={(e) => {
                    e.preventDefault();
                    handleSend();
                }}
                className="flex items-center gap-2 pt-3 border-t border-stone-100 dark:border-stone-800"
            >
                <input
                    type="text"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    placeholder="Ask anything about this artwork..."
                    disabled={loading}
                    className="flex-1 text-xs md:text-sm px-4 py-3 rounded-full border border-stone-200 dark:border-stone-700 bg-stone-50 dark:bg-stone-800 text-stone-900 dark:text-stone-100 focus:outline-none focus:ring-2 focus:ring-amber-600 transition"
                />
                <button
                    type="submit"
                    disabled={!input.trim() || loading}
                    className="p-3 rounded-full bg-amber-600 hover:bg-amber-700 text-white disabled:opacity-40 transition shadow-md cursor-pointer active:scale-95"
                    title="Send Question"
                >
                    <Send className="w-4 h-4" />
                </button>
            </form>
        </div>
    );
}