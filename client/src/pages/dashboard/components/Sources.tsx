import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Link, ExternalLink } from "lucide-react";

interface SourcesProps {
    urls: string[];
    sourcesData?: Array<{
        title: string;
        url: string;
        published_date?: string;
        relevance_score?: number;
    }>;
}

export function Sources({ urls, sourcesData }: SourcesProps) {
    return (
        <Card>
            <CardHeader>
                <CardTitle className="flex items-center">
                    <Link className="mr-2 h-5 w-5" />
                    Sources ({urls.length})
                </CardTitle>
            </CardHeader>
            <CardContent className="max-h-96 overflow-y-auto">
                <ul className="space-y-3">
                    {sourcesData && sourcesData.length > 0 ? (
                        sourcesData.map((source, index) => (
                            <li key={index} className="border-b last:border-0 pb-3 last:pb-0">
                                <a
                                    href={source.url}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="block rounded-md p-2 hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors"
                                >
                                    <div className="flex items-start justify-between gap-2">
                                        <div className="flex-1 min-w-0">
                                            <div className="flex items-center gap-2 mb-1">
                                                <img
                                                    src={`https://www.google.com/s2/favicons?sz=64&domain_url=${source.url}`}
                                                    alt="favicon"
                                                    className="h-4 w-4 flex-shrink-0"
                                                />
                                                <span className="text-xs text-slate-500 dark:text-slate-400 truncate">
                                                    {new URL(source.url).hostname}
                                                </span>
                                            </div>
                                            <p className="text-sm font-medium text-slate-900 dark:text-slate-100 line-clamp-2">
                                                {source.title}
                                            </p>
                                            {source.published_date && (
                                                <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
                                                    {new Date(source.published_date).toLocaleDateString()}
                                                </p>
                                            )}
                                            {source.relevance_score !== undefined && (
                                                <p className="text-xs text-blue-600 dark:text-blue-400 mt-1">
                                                    Relevance: {(source.relevance_score * 100).toFixed(0)}%
                                                </p>
                                            )}
                                        </div>
                                        <ExternalLink className="h-4 w-4 text-slate-400 flex-shrink-0 mt-1" />
                                    </div>
                                </a>
                            </li>
                        ))
                    ) : (
                        urls.map((url, index) => (
                            <li key={index}>
                                <a
                                    href={url}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="flex items-center justify-between rounded-md p-2 hover:bg-slate-100 dark:hover:bg-slate-700"
                                >
                                    <div className="flex items-center">
                                        <img
                                            src={`https://www.google.com/s2/favicons?sz=64&domain_url=${url}`}
                                            alt="favicon"
                                            className="mr-3 h-6 w-6"
                                        />
                                        <span className="text-sm font-medium">
                                            {new URL(url).hostname}
                                        </span>
                                    </div>
                                    <ExternalLink className="h-4 w-4 text-slate-500" />
                                </a>
                            </li>
                        ))
                    )}
                </ul>
            </CardContent>
        </Card>
    );
}
