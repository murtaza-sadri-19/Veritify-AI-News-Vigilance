import { Button } from "@/components/ui/button";
import {
    Card,
    CardContent,
    CardDescription,
    CardHeader,
    CardTitle,
} from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import {
    Accordion,
    AccordionContent,
    AccordionItem,
    AccordionTrigger,
} from "@/components/ui/accordion";
import { Input } from "@/components/ui/input";
import { Loader2 } from "lucide-react";
import { useState } from "react";

interface FactCheckFormProps {
    onVerify: (claim: string, apiKey?: string) => void;
    isLoading?: boolean;
}

export function FactCheckForm({ onVerify, isLoading = false }: FactCheckFormProps) {
    const [claim, setClaim] = useState("");
    const [apiKey, setApiKey] = useState("");

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        onVerify(claim, apiKey || undefined);
    };

    return (
        <Card className="mx-auto max-w-4xl">
            <CardHeader>
                <CardTitle className="text-2xl font-bold">Fact Check Claims</CardTitle>
                <CardDescription>
                    Enter a claim to verify its credibility against reliable news sources.
                </CardDescription>
            </CardHeader>
            <CardContent>
                <form onSubmit={handleSubmit} className="space-y-6">
                    <Textarea
                        placeholder="e.g., The Eiffel Tower was painted green in 2025..."
                        className="min-h-[150px] text-base"
                        value={claim}
                        onChange={(e) => setClaim(e.target.value)}
                        disabled={isLoading}
                    />
                    <Accordion type="single" collapsible>
                        <AccordionItem value="item-1">
                            <AccordionTrigger>Advanced Settings</AccordionTrigger>
                            <AccordionContent>
                                <Input 
                                    placeholder="Enter your API Key (optional)" 
                                    value={apiKey}
                                    onChange={(e) => setApiKey(e.target.value)}
                                    disabled={isLoading}
                                />
                            </AccordionContent>
                        </AccordionItem>
                    </Accordion>
                    <Button type="submit" className="w-full" disabled={isLoading || !claim.trim()}>
                        {isLoading ? (
                            <>
                                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                Verifying...
                            </>
                        ) : (
                            "Verify"
                        )}
                    </Button>
                </form>
            </CardContent>
        </Card>
    );
}
