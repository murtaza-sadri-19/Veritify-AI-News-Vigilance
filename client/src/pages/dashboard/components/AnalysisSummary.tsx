import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { FileText, CheckCircle2, AlertCircle, Info } from "lucide-react";

interface AnalysisSummaryProps {
    summary: string;
    strengths?: string[];
    weaknesses?: string[];
    context?: string;
}

export function AnalysisSummary({ summary, strengths, weaknesses, context }: AnalysisSummaryProps) {
    return (
        <Card>
            <CardHeader>
                <CardTitle className="flex items-center">
                    <FileText className="mr-2 h-5 w-5" />
                    Analysis
                </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
                <div>
                    <p className="text-sm text-gray-700 dark:text-gray-300">{summary}</p>
                </div>
                
                {strengths && strengths.length > 0 && (
                    <div>
                        <h4 className="flex items-center font-semibold text-green-600 dark:text-green-400 mb-2">
                            <CheckCircle2 className="mr-2 h-4 w-4" />
                            Strengths
                        </h4>
                        <ul className="list-disc list-inside space-y-1 text-sm">
                            {strengths.map((strength, index) => (
                                <li key={index} className="text-gray-600 dark:text-gray-400">
                                    {strength}
                                </li>
                            ))}
                        </ul>
                    </div>
                )}

                {weaknesses && weaknesses.length > 0 && (
                    <div>
                        <h4 className="flex items-center font-semibold text-amber-600 dark:text-amber-400 mb-2">
                            <AlertCircle className="mr-2 h-4 w-4" />
                            Weaknesses
                        </h4>
                        <ul className="list-disc list-inside space-y-1 text-sm">
                            {weaknesses.map((weakness, index) => (
                                <li key={index} className="text-gray-600 dark:text-gray-400">
                                    {weakness}
                                </li>
                            ))}
                        </ul>
                    </div>
                )}

                {context && (
                    <div>
                        <h4 className="flex items-center font-semibold text-blue-600 dark:text-blue-400 mb-2">
                            <Info className="mr-2 h-4 w-4" />
                            Context
                        </h4>
                        <p className="text-sm text-gray-600 dark:text-gray-400">{context}</p>
                    </div>
                )}
            </CardContent>
        </Card>
    );
}
