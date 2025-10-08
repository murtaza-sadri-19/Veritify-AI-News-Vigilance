import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { motion } from "framer-motion";

interface CredibilityScoreProps {
    score: number;
    verdict?: string;
}

const getScoreColor = (score: number) => {
    if (score < 40) return "#DC2626"; // Red
    if (score < 60) return "#F59E0B"; // Amber
    return "#16A34A"; // Green
};

const getScoreLabel = (score: number) => {
    if (score < 40) return "Likely False";
    if (score < 60) return "Mixed";
    if (score < 80) return "Likely Credible";
    return "Highly Credible";
};

export function CredibilityScore({ score, verdict }: CredibilityScoreProps) {
    const color = getScoreColor(score);
    const label = verdict || getScoreLabel(score);
    const circumference = 2 * Math.PI * 45;
    const offset = circumference - (score / 100) * circumference;

    return (
        <Card>
            <CardHeader>
                <CardTitle>Credibility Score</CardTitle>
            </CardHeader>
            <CardContent className="flex flex-col items-center justify-center">
                <div className="relative h-40 w-40">
                    <svg className="h-full w-full" viewBox="0 0 100 100">
                        <circle
                            cx="50"
                            cy="50"
                            r="45"
                            className="stroke-current text-slate-200 dark:text-slate-700"
                            strokeWidth="10"
                            fill="transparent"
                        />
                        <motion.circle
                            cx="50"
                            cy="50"
                            r="45"
                            className="stroke-current"
                            strokeWidth="10"
                            fill="transparent"
                            strokeDasharray={circumference}
                            strokeDashoffset={offset}
                            strokeLinecap="round"
                            transform="rotate(-90 50 50)"
                            style={{ color }}
                            initial={{ strokeDashoffset: circumference }}
                            animate={{ strokeDashoffset: offset }}
                            transition={{ duration: 1, ease: "easeOut" }}
                        />
                    </svg>
                    <div className="absolute inset-0 flex items-center justify-center">
                        <span className="text-4xl font-bold" style={{ color }}>
                            {score}
                        </span>
                    </div>
                </div>
                <p className="mt-4 text-lg font-semibold" style={{ color }}>
                    {label}
                </p>
            </CardContent>
        </Card>
    );
}
