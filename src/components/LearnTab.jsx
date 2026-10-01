import React, { useState } from 'react';
import { HelpCircle, CheckCircle2, XCircle, Lightbulb } from 'lucide-react';

export default function LearnTab({ learning }) {
    const [selectedAnswers, setSelectedAnswers] = useState({});
    const [revealedExplanations, setRevealedExplanations] = useState({});

    const handleSelectOption = (qIndex, optionIndex) => {
        setSelectedAnswers({ ...selectedAnswers, [qIndex]: optionIndex });
        setRevealedExplanations({ ...revealedExplanations, [qIndex]: true });
    };

    return (
        <div className="space-y-8 animate-fade-in">
            <div className="space-y-3">
                <h3 className="text-xs uppercase tracking-widest font-semibold text-stone-500 dark:text-stone-400">
                    Core Artistic Concepts
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                    {learning?.key_points?.map((point, idx) => (
                        <div key={idx} className="p-4 rounded-xl border border-stone-200 dark:border-stone-800 bg-white dark:bg-stone-900 flex items-start gap-3">
                            <Lightbulb className="w-4 h-4 text-amber-600 flex-shrink-0 mt-0.5" />
                            <p className="text-xs leading-relaxed text-stone-700 dark:text-stone-300">{point}</p>
                        </div>
                    ))}
                </div>
            </div>

            {learning?.quiz?.length > 0 && (
                <div className="space-y-4">
                    <div className="flex items-center gap-2">
                        <HelpCircle className="w-4 h-4 text-amber-600" />
                        <h3 className="text-xs uppercase tracking-widest font-semibold text-stone-500 dark:text-stone-400">
                            Interactive Observation Challenge
                        </h3>
                    </div>

                    <div className="space-y-4">
                        {learning.quiz.map((q, qIdx) => {
                            const selectedOpt = selectedAnswers[qIdx];
                            const isAnswered = selectedOpt !== undefined;

                            return (
                                <div key={qIdx} className="p-5 rounded-xl border border-stone-200 dark:border-stone-800 bg-white dark:bg-stone-900 space-y-4">
                                    <h4 className="font-serif text-base font-medium text-stone-900 dark:text-stone-100">
                                        {qIdx + 1}. {q.question}
                                    </h4>

                                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                                        {q.options.map((opt, oIdx) => {
                                            const isCorrect = oIdx === q.correctIndex;
                                            const isChosen = selectedOpt === oIdx;

                                            let btnStyle = 'border-stone-200 dark:border-stone-700 hover:border-stone-400';
                                            if (isAnswered) {
                                                if (isCorrect) btnStyle = 'border-emerald-600 bg-emerald-50 dark:bg-emerald-950/40 text-emerald-900 dark:text-emerald-200';
                                                else if (isChosen) btnStyle = 'border-rose-600 bg-rose-50 dark:bg-rose-950/40 text-rose-900 dark:text-rose-200';
                                            }

                                            return (
                                                <button
                                                    key={oIdx}
                                                    disabled={isAnswered}
                                                    onClick={() => handleSelectOption(qIdx, oIdx)}
                                                    className={`text-left p-3 rounded-lg border text-xs font-medium transition flex items-center justify-between ${btnStyle}`}
                                                >
                                                    <span>{opt}</span>
                                                    {isAnswered && isCorrect && <CheckCircle2 className="w-4 h-4 text-emerald-600" />}
                                                    {isAnswered && isChosen && !isCorrect && <XCircle className="w-4 h-4 text-rose-600" />}
                                                </button>
                                            );
                                        })}
                                    </div>

                                    {revealedExplanations[qIdx] && q.explanation && (
                                        <div className="text-xs p-3 rounded-lg bg-stone-100 dark:bg-stone-800 text-stone-700 dark:text-stone-300">
                                            <strong>AI Explanation:</strong> {q.explanation}
                                        </div>
                                    )}
                                </div>
                            );
                        })}
                    </div>
                </div>
            )}
        </div>
    );
}