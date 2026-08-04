import React from 'react';
import { ShieldAlert, CheckCircle, TrendingUp, Newspaper, ArrowUpRight } from 'lucide-react';

// ============================================================================
// MOCK DATA - Use this to test the component immediately
// ============================================================================
const MOCK_DATA = {
    isFalse: true, // Toggle to false to see the "TRUE" state
    claimText: "Climate change is a hoax.",
    confidenceScore: 92,
    sources: [
        {
            id: 1,
            name: "Scientific American",
            date: "Mar 7, 2023",
            type: "Refutes",
            snippet: "Climate change is a hoax, what icant rounded-xl hover:shadow-lg hover:border-blue-400 transition-all group...",
            url: "#"
        },
        {
            id: 2,
            name: "NASA Climate Report",
            date: "Feb 8, 2022",
            type: "Refutes",
            snippet: "Climate change is a hoax, what icant rounded-xl hover:shadow-lg hover:border-blue-400 transition-all group...",
            url: "#"
        },
        {
            id: 3,
            name: "IPCC Assessment",
            date: "Jan 15, 2023",
            type: "Refutes",
            snippet: "Comprehensive scientific evidence demonstrates that human activities are driving unprecedented climate shifts globally...",
            url: "#"
        },
        {
            id: 4,
            name: "Nature Journal",
            date: "Dec 3, 2022",
            type: "Refutes",
            snippet: "Peer-reviewed research confirms the reality of anthropogenic climate change through multiple independent data sources...",
            url: "#"
        }
    ]
};

// ============================================================================
// MAIN COMPONENT
// ============================================================================
const VerificationDashboard = ({ data = MOCK_DATA }) => {
    const { isFalse, claimText, confidenceScore, sources } = data;

    return (
        <div className="min-h-screen bg-gray-50 py-12 px-4">
            <div className="max-w-4xl mx-auto space-y-8 p-4">

                {/* ================================================================== */}
                {/* ZONE 1: The Verdict Banner */}
                {/* ================================================================== */}
                <div
                    className={`rounded-xl border-l-[8px] p-8 shadow-sm flex items-start gap-6 ${isFalse ? 'bg-red-50 border-red-600' : 'bg-green-50 border-green-600'
                        }`}
                >
                    {/* Icon - LOCKED SIZE */}
                    <div className={`p-3 rounded-full ${isFalse ? 'bg-red-100' : 'bg-green-100'}`}>
                        {isFalse ? (
                            <ShieldAlert className="w-10 h-10 text-red-600" />
                        ) : (
                            <CheckCircle className="w-10 h-10 text-green-600" />
                        )}
                    </div>
                    <div>
                        <h1
                            className={`text-4xl font-black uppercase tracking-tight mb-2 ${isFalse ? 'text-red-700' : 'text-green-700'
                                }`}
                        >
                            {isFalse ? 'Claim Proven False' : 'Claim Confirmed True'}
                        </h1>
                        <p className="text-xl text-gray-700 font-medium">
                            Claim: <span className="italic text-gray-600">"{claimText}"</span>
                        </p>
                    </div>
                </div>

                {/* ================================================================== */}
                {/* ZONE 2: The "Trust Metrics" Grid */}
                {/* ================================================================== */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">

                    {/* Card 1: Confidence Score */}
                    <div className="bg-white border border-gray-200 rounded-xl p-6 shadow-sm flex flex-col justify-between">
                        <div className="flex items-center gap-2 text-gray-500 mb-2">
                            <TrendingUp className="w-5 h-5" />
                            <span className="font-semibold text-sm uppercase tracking-wider">AI Confidence</span>
                        </div>
                        <div className="text-5xl font-black text-gray-900 mb-4">{confidenceScore}%</div>
                        {/* Progress Bar */}
                        <div className="w-full bg-gray-100 h-3 rounded-full overflow-hidden">
                            <div
                                className={`h-full rounded-full ${isFalse ? 'bg-red-500' : 'bg-green-500'}`}
                                style={{ width: `${confidenceScore}%` }}
                            />
                        </div>
                    </div>

                    {/* Card 2: Source Count */}
                    <div className="bg-white border border-gray-200 rounded-xl p-6 shadow-sm">
                        <p className="text-gray-500 font-semibold text-sm uppercase tracking-wider mb-2">
                            Sources Analyzed
                        </p>
                        <p className="text-4xl font-bold text-gray-900">24</p>
                        <p className="text-sm text-gray-400 mt-2">Across 12 global regions</p>
                    </div>

                    {/* Card 3: Bias Metric */}
                    <div className="bg-white border border-gray-200 rounded-xl p-6 shadow-sm">
                        <p className="text-gray-500 font-semibold text-sm uppercase tracking-wider mb-2">
                            Bias Leaning
                        </p>
                        <p className="text-2xl font-bold text-gray-900">Neutral / Scientific</p>
                        <div className="flex gap-1 mt-3">
                            <div className="h-2 flex-1 bg-blue-200 rounded-l-full"></div>
                            <div className="h-2 flex-1 bg-gray-400"></div>
                            <div className="h-2 flex-1 bg-red-200 rounded-r-full"></div>
                        </div>
                    </div>
                </div>

                {/* ================================================================== */}
                {/* ZONE 3: Evidence Grid */}
                {/* ================================================================== */}
                <div>
                    <h3 className="text-xs font-bold text-gray-400 uppercase tracking-[0.2em] mb-6">
                        Primary Evidence Sources
                    </h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {sources.map((source) => (
                            <div
                                key={source.id}
                                className="group bg-white border border-gray-200 rounded-lg p-5 hover:border-blue-400 hover:shadow-md transition-all cursor-pointer"
                            >
                                <div className="flex justify-between items-start mb-3">
                                    <div>
                                        <p className="font-bold text-gray-900">{source.name}</p>
                                        <p className="text-xs text-gray-500">{source.date}</p>
                                    </div>
                                    <span
                                        className={`px-2 py-1 rounded text-xs font-bold ${source.type === 'Refutes'
                                                ? 'bg-red-100 text-red-700'
                                                : 'bg-green-100 text-green-700'
                                            }`}
                                    >
                                        {source.type}
                                    </span>
                                </div>
                                <p className="text-sm text-gray-600 line-clamp-3 leading-relaxed mb-4">
                                    {source.snippet}
                                </p>
                                <div className="flex items-center text-blue-600 font-semibold text-xs group-hover:underline">
                                    Read Full Report <ArrowUpRight className="w-3 h-3 ml-1" />
                                </div>
                            </div>
                        ))}
                    </div>
                </div>

            </div>
        </div>
    );
};

export default VerificationDashboard;
