import { motion } from "framer-motion";
import { CredibilityScore } from "./CredibilityScore";
import { AnalysisSummary } from "./AnalysisSummary";
import { Sources } from "./Sources";

interface ResultsSectionProps {
    result: {
        claim: string;
        credibility_score: number;
        verdict: string;
        summary: string;
        sources: Array<{
            title: string;
            url: string;
            published_date?: string;
            relevance_score?: number;
        }>;
        analysis: {
            strengths: string[];
            weaknesses: string[];
            context: string;
        };
    };
}

export function ResultsSection({ result }: ResultsSectionProps) {
    const score = result.credibility_score;
    const analysis = result.summary;
    const sources = result.sources.map(source => source.url);

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="mt-8 grid grid-cols-1 gap-8 lg:grid-cols-3"
        >
            <CredibilityScore score={score} verdict={result.verdict} />
            <AnalysisSummary 
                summary={analysis} 
                strengths={result.analysis.strengths}
                weaknesses={result.analysis.weaknesses}
                context={result.analysis.context}
            />
            <Sources urls={sources} sourcesData={result.sources} />
        </motion.div>
    );
}
