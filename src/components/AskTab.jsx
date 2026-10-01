import React, { useState } from 'react';
import { Send, Bot, User, Loader2 } from 'lucide-react';
import { askArtwork } from '../api/kalakathaApi';

const SUGGESTIONS = [
    "Why does this artwork feel peaceful?",
    "What artistic technique is being used?",
    "What is happening in the background?",
    "Explain this artwork like I am 10."
];

export default function AskTab({ artworkId, isMock }) {
    const [messages, setMessages] = useState([
        {
            sender: 'guide',
            text: "I am your KalaKatha art companion for this piece. Ask me anything about its brushwork, hidden symbols, or historical mysteries."
        }
    ]);
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);

    const handleSend = async (queryText) => {
        const question = queryText || input;
        if (!question.trim() || loading) return;

        const userMessage = { sender: 'user', text: question };
        setMessages((prev) => [...prev, userMessage]);
        setInput('');
        setLoading(true);

        try {
            if (isMock) {
                await new Promise((r) => setTimeout(r, 900));
                setMessages((prev) => [
                    ...prev,
                    {
                        sender: 'guide',
                        text: `Regarding "${question}": The master intentionally balances contrast and spatial weight here to guide your eye directly into the heart of the canvas.`
                    }
                ]);
            } else {
                const response = await askArtwork(artworkId, question);
                setMessages((prev) => [
                    ...prev,
                    { sender: 'guide', text: response.answer || 'Thank you for your question.' }
                ]);
            }
        } catch (err) {
            setMessages((prev) => [
                ...prev,
                { sender: 'guide', text: `Error: ${err.message}` }
            ]);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="space-y-4 flex flex-col h-[520px] rounded-2xl border border-stone-200 dark:border-stone-800 bg-white dark:bg-stone-900 p-4 shadow-sm animate-fade-in">
            <div className="flex gap-2 overflow-x-auto pb-2 border-b border-stone-100 dark:border-stone-800 scrollbar-none">
                {SUGGESTIONS.map((s, i) => (
                    <button
                        key={i}
                        onClick={() => handleSend(s)}
                        className="text-[11px] whitespace-nowrap px-3 py-1.5 rounded-full bg-stone-100 dark:bg-stone-800 text-stone-600 dark:text-stone-300 hover:border-amber-600 border border-transparent transition"
                    >
                        {s}
                    </button>
                ))}
            </div>

            <div className="flex-1 overflow-y-auto space-y-4 pr-2">
                {messages.map((m, idx) => (
                    <div
                        key={idx}
                        className={`flex gap-3 ${m.sender === 'user' ? 'justify-end' : 'justify-start'}`}
                    >
                        {m.sender === 'guide' && (
                            <div className="w-7 h-7 rounded-full bg-amber-600 text-white flex items-center justify-center flex-shrink-0 mt-0.5">
                                <Bot className="w-4 h-4" />
                            </div>
                        )}
                        <div
                            className={`max-w-[80%] rounded-2xl px-4 py-2.5 text-xs md:text-sm leading-relaxed ${m.sender === 'user'
                                    ? 'bg-stone-900 dark:bg-stone-100 text-white dark:text-stone-900'
                                    : 'bg-stone-100 dark:bg-stone-800/80 text-stone-800 dark:text-stone-200'
                                }`}
                        >
                            {m.text}
                        </div>
                        {m.sender === 'user' && (
                            <div className="w-7 h-7 rounded-full bg-stone-300 dark:bg-stone-700 text-stone-700 dark:text-stone-200 flex items-center justify-center flex-shrink-0 mt-0.5">
                                <User className="w-4 h-4" />
                            </div>
                        )}
                    </div>
                ))}
                {loading && (
                    <div className="flex items-center gap-2 text-xs text-stone-500">
                        <Loader2 className="w-4 h-4 animate-spin text-amber-600" />
                        <span>Consulting Ask Agent...</span>
                    </div>
                )}
            </div>

            <form
                onSubmit={(e) => {
                    e.preventDefault();
                    handleSend();
                }}
                className="flex items-center gap-2 pt-2 border-t border-stone-100 dark:border-stone-800"
            >
                <input
                    type="text"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    placeholder="Ask a question about this artwork..."
                    className="flex-1 text-xs md:text-sm px-4 py-2.5 rounded-full border border-stone-200 dark:border-stone-700 bg-stone-50 dark:bg-stone-800 text-stone-900 dark:text-stone-100 focus:outline-none focus:ring-1 focus:ring-amber-600"
                />
                <button
                    type="submit"
                    disabled={!input.trim() || loading}
                    className="p-2.5 rounded-full bg-amber-600 hover:bg-amber-700 text-white disabled:opacity-40 transition"
                >
                    <Send className="w-4 h-4" />
                </button>
            </form>
        </div>
    );
}