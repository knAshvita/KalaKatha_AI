import React, { useState } from 'react';
import { HelpCircle, CheckCircle2, XCircle, Lightbulb, Sparkles, Award, Loader2, AlertCircle } from 'lucide-react';
import { submitQuizAnswer } from '../api/kalakathaApi';

export default function LearnTab({ learning, sessionId }) {
    // Dynamic quiz state evaluated by the server
    const [selectedAnswers, setSelectedAnswers] = useState({});
    const [evaluations, setEvaluations] = useState({});
    const [submittingQuestionId, setSubmittingQuestionId] = useState(null);
    const [quizError, setQuizError] = useState(null);

    // Normalize concepts and did-you-know facts
    const concepts = learning?.key_concepts || learning?.key_points || [];
    const explanations = Array.isArray(learning?.simple_explanations)
        ? learning.simple_explanations
        : (typeof learning?.simple_explanations === 'object' && learning?.simple_explanations !== null
            ? Object.values(learning.simple_explanations)
            : []);
    const interestingFacts = learning?.interesting_facts || [];
    const thingsToNotice = learning?.things_to_notice || [];

    // Combine concepts and explanations for clean card display
    const conceptCards = concepts.map((concept, idx) => {
        const explanation = explanations[idx] || (interestingFacts[idx] || "Key element of the composition and technique.");
        return { concept, explanation };
    });

    // Normalize quiz questions
    const rawQuestions = learning?.multiple_choice_questions || learning?.quiz || [];
    const questions = rawQuestions.map((q, idx) => ({
        id: q.question_id || q.id || `q${idx + 1}`,
        question: q.question,
        options: q.options || [],
        fallbackExplanation: q.explanation || ''
    }));

    const handleSelectOption = async (questionId, optionText) => {
        if (evaluations[questionId] || submittingQuestionId) return;

        setSelectedAnswers((prev) => ({ ...prev, [questionId]: optionText }));
        setSubmittingQuestionId(questionId);
        setQuizError(null);

        try {
            if (!sessionId) {
                throw new Error("Session ID is required to verify quiz answer.");
            }

            const response = await submitQuizAnswer(sessionId, questionId, optionText);
            setEvaluations((prev) => ({
                ...prev,
                [questionId]: {
                    isCorrect: response.is_correct,
                    correctOption: response.correct_option,
                    explanation: response.explanation || 'Verified by KalaKatha backend.'
                }
            }));
        } catch (err) {
            setQuizError(`Could not verify answer with server: ${err.message}`);
        } finally {
            setSubmittingQuestionId(null);
        }
    };

    const answeredCount = Object.keys(evaluations).length;
    const correctCount = Object.values(evaluations).filter(e => e.isCorrect).length;

    return (
        <div className="space-y-8 animate-fade-in text-stone-800 dark:text-stone-200">

            {/* 1. Core Artistic Concepts & Observations */}
            <div className="space-y-4">
                <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2 text-xs uppercase tracking-widest font-semibold text-amber-700 dark:text-amber-400">
                        <Lightbulb className="w-4 h-4 text-amber-600" />
                        <span>Core Artistic Concepts</span>
                    </div>
                    <span className="text-[11px] text-stone-400">Derived from Artwork Analysis</span>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                    {conceptCards.map((item, idx) => (
                        <div
                            key={idx}
                            className="p-4 rounded-2xl border border-stone-200/90 dark:border-stone-800 bg-white dark:bg-stone-900 shadow-2xs space-y-1.5"
                        >
                            <div className="flex items-center gap-2">
                                <Sparkles className="w-3.5 h-3.5 text-amber-600 flex-shrink-0" />
                                <h4 className="font-serif font-bold text-sm text-stone-900 dark:text-stone-100">
                                    {item.concept}
                                </h4>
                            </div>
                            <p className="text-xs leading-relaxed text-stone-600 dark:text-stone-300 font-serif">
                                {item.explanation}
                            </p>
                        </div>
                    ))}
                </div>

                {/* Things to Notice & Did-You-Know Pill Box */}
                {(interestingFacts.length > 0 || thingsToNotice.length > 0) && (
                    <div className="p-5 rounded-2xl border border-amber-300/60 dark:border-amber-900/40 bg-amber-50/50 dark:bg-amber-950/20 space-y-3">
                        <span className="text-[11px] uppercase tracking-wider font-bold text-amber-800 dark:text-amber-300 block">
                            Curator’s Observations & Facts
                        </span>
                        <div className="space-y-2">
                            {interestingFacts.slice(0, 3).map((fact, fIdx) => (
                                <p key={fIdx} className="text-xs text-stone-700 dark:text-stone-300 font-serif flex items-start gap-2">
                                    <span className="text-amber-600 font-bold">•</span>
                                    <span>{fact}</span>
                                </p>
                            ))}
                        </div>
                    </div>
                )}
            </div>

            {/* 2. Dynamic Multiple-Choice Quiz */}
            {questions.length > 0 && (
                <div className="space-y-4 pt-2">
                    <div className="flex items-center justify-between flex-wrap gap-2">
                        <div className="flex items-center gap-2">
                            <HelpCircle className="w-4 h-4 text-amber-600" />
                            <h3 className="text-xs uppercase tracking-widest font-semibold text-stone-500 dark:text-stone-400">
                                Dynamic Observation Quiz
                            </h3>
                        </div>

                        {answeredCount > 0 && (
                            <div className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-stone-100 dark:bg-stone-800 border border-stone-200 dark:border-stone-700 text-xs font-semibold">
                                <Award className="w-3.5 h-3.5 text-amber-600" />
                                <span>Score: {correctCount} / {questions.length}</span>
                            </div>
                        )}
                    </div>

                    {quizError && (
                        <div className="flex items-center gap-2 text-xs text-rose-700 bg-rose-50 dark:bg-rose-950/40 p-3 rounded-xl border border-rose-200 dark:border-rose-900">
                            <AlertCircle className="w-4 h-4 text-rose-600 flex-shrink-0" />
                            <span>{quizError}</span>
                        </div>
                    )}

                    <div className="space-y-4">
                        {questions.map((q, qIdx) => {
                            const chosenOption = selectedAnswers[q.id];
                            const evaluation = evaluations[q.id];
                            const isAnswered = evaluation !== undefined;
                            const isSubmittingThis = submittingQuestionId === q.id;

                            return (
                                <div
                                    key={q.id || qIdx}
                                    className="p-5 rounded-3xl border border-stone-200/90 dark:border-stone-800 bg-white dark:bg-stone-900 space-y-4 shadow-sm"
                                >
                                    <div className="flex items-start justify-between gap-3">
                                        <h4 className="font-serif text-base sm:text-lg font-bold text-stone-900 dark:text-stone-100">
                                            {qIdx + 1}. {q.question}
                                        </h4>
                                        {isSubmittingThis && (
                                            <Loader2 className="w-4 h-4 animate-spin text-amber-600 flex-shrink-0 mt-1" />
                                        )}
                                    </div>

                                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
                                        {q.options.map((opt, oIdx) => {
                                            const isSelected = chosenOption === opt;
                                            const isCorrectOption = evaluation?.correctOption === opt;

                                            let btnClasses = "border-stone-200 dark:border-stone-700 hover:border-amber-500 hover:bg-stone-50 dark:hover:bg-stone-800 text-stone-700 dark:text-stone-200";

                                            if (isAnswered) {
                                                if (isCorrectOption) {
                                                    btnClasses = "border-emerald-500 bg-emerald-50 dark:bg-emerald-950/40 text-emerald-900 dark:text-emerald-200 font-semibold ring-1 ring-emerald-500";
                                                } else if (isSelected && !evaluation.isCorrect) {
                                                    btnClasses = "border-rose-500 bg-rose-50 dark:bg-rose-950/40 text-rose-900 dark:text-rose-200 font-semibold ring-1 ring-rose-500";
                                                } else {
                                                    btnClasses = "opacity-50 border-stone-200 dark:border-stone-800 text-stone-400";
                                                }
                                            }

                                            return (
                                                <button
                                                    key={oIdx}
                                                    type="button"
                                                    disabled={isAnswered || isSubmittingThis}
                                                    onClick={() => handleSelectOption(q.id, opt)}
                                                    className={`text-left p-3.5 rounded-xl border text-xs leading-relaxed transition-all duration-200 flex items-center justify-between gap-2 cursor-pointer ${btnClasses}`}
                                                >
                                                    <span className="font-serif">{opt}</span>
                                                    {isAnswered && isCorrectOption && (
                                                        <CheckCircle2 className="w-4 h-4 text-emerald-600 flex-shrink-0" />
                                                    )}
                                                    {isAnswered && isSelected && !evaluation.isCorrect && (
                                                        <XCircle className="w-4 h-4 text-rose-600 flex-shrink-0" />
                                                    )}
                                                </button>
                                            );
                                        })}
                                    </div>

                                    {/* Server Explanation Banner */}
                                    {isAnswered && evaluation && (
                                        <div className={`text-xs p-3.5 rounded-xl border leading-relaxed font-serif ${
                                            evaluation.isCorrect
                                                ? 'bg-emerald-50/70 dark:bg-emerald-950/30 border-emerald-300 dark:border-emerald-900/60 text-emerald-950 dark:text-emerald-200'
                                                : 'bg-amber-50/70 dark:bg-amber-950/30 border-amber-300 dark:border-amber-900/60 text-amber-950 dark:text-amber-200'
                                        }`}>
                                            <span className="font-sans font-bold uppercase tracking-wider text-[10px] block mb-0.5">
                                                {evaluation.isCorrect ? 'Correct Analysis' : 'Curator Note'}
                                            </span>
                                            {evaluation.explanation}
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