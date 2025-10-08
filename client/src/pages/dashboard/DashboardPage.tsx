import { Header } from "./components/Header";
import { FactCheckForm } from "./components/FactCheckForm";
import { ResultsSection } from "./components/ResultsSection";
import { ResultsSkeleton } from "./components/ResultsSkeleton";
import { useState } from "react";
import { verifyClaimAPI, FactCheckResult } from "@/services/api";
import toast from "react-hot-toast";

export function DashboardPage() {
    const [isVerifying, setIsVerifying] = useState(false);
    const [resultsVisible, setResultsVisible] = useState(false);
    const [factCheckResult, setFactCheckResult] = useState<FactCheckResult | null>(null);

    const handleVerification = async (claim: string, apiKey?: string) => {
        if (!claim.trim()) {
            toast.error("Please enter a claim to verify");
            return;
        }

        setIsVerifying(true);
        setResultsVisible(false);
        setFactCheckResult(null);

        try {
            const result = await verifyClaimAPI(claim, apiKey);
            
            if (result.success && result.result) {
                setFactCheckResult(result);
                setResultsVisible(true);
                toast.success("Fact-check completed!");
            } else {
                throw new Error(result.error || "Failed to verify claim");
            }
        } catch (error) {
            console.error("Verification error:", error);
            toast.error(error instanceof Error ? error.message : "Failed to verify claim");
        } finally {
            setIsVerifying(false);
        }
    };

    return (
        <div className="min-h-screen bg-slate-100 dark:bg-slate-900">
            <Header />
            <main className="container mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
                <FactCheckForm onVerify={handleVerification} isLoading={isVerifying} />
                {isVerifying && <ResultsSkeleton />}
                {resultsVisible && factCheckResult?.result && (
                    <ResultsSection result={factCheckResult.result} />
                )}
            </main>
        </div>
    );
}