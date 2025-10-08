import { Button } from "@/components/ui/button";
import {
    Card,
    CardContent,
    CardDescription,
    CardFooter,
    CardHeader,
    CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Mail, Loader2 } from "lucide-react";
import { Link } from "react-router-dom";
import { useState } from "react";
import { useAuth } from "@/contexts/AuthContext";
import toast from "react-hot-toast";

export function ForgotPasswordPage() {
    const { resetPassword } = useAuth();
    const [email, setEmail] = useState("");
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");
    const [success, setSuccess] = useState(false);

    const handleResetPassword = async (e: React.FormEvent) => {
        e.preventDefault();
        
        if (!email) {
            setError("Please enter your email");
            toast.error("Please enter your email");
            return;
        }

        try {
            setError("");
            setSuccess(false);
            setLoading(true);
            await resetPassword(email);
            setSuccess(true);
            toast.success("Password reset link sent! Check your email.");
            setEmail("");
        } catch (err: any) {
            console.error("Password reset error:", err);
            let errorMessage = "Failed to send reset email";
            
            if (err.code === "auth/user-not-found") {
                errorMessage = "No account found with this email";
            } else if (err.code === "auth/invalid-email") {
                errorMessage = "Invalid email address";
            } else if (err.code === "auth/too-many-requests") {
                errorMessage = "Too many requests. Please try again later";
            }
            
            setError(errorMessage);
            toast.error(errorMessage);
        } finally {
            setLoading(false);
        }
    };
    return (
        <div className="flex h-screen">
            <div className="hidden lg:flex lg:w-2/5 flex-col items-center justify-center bg-gradient-to-br from-blue-600 to-purple-600 text-white p-8">
                <h1 className="text-4xl font-bold">TruthTrack</h1>
                <p className="mt-4 text-lg text-center">
                    Navigate Information with Confidence.
                </p>
            </div>
            <div className="w-full lg:w-3/5 flex items-center justify-center p-8">
                <Card className="w-full max-w-md">
                    <CardHeader>
                        <CardTitle className="text-2xl">Reset Password</CardTitle>
                        <CardDescription>
                            Enter your email to receive a password reset link.
                        </CardDescription>
                        {error && (
                            <div className="text-sm text-red-600 mt-2 p-2 bg-red-50 rounded">
                                {error}
                            </div>
                        )}
                        {success && (
                            <div className="text-sm text-green-600 mt-2 p-2 bg-green-50 rounded">
                                Password reset link sent! Check your email inbox.
                            </div>
                        )}
                    </CardHeader>
                    <CardContent className="space-y-4">
                        <div className="relative">
                            <Mail className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
                            <Input 
                                type="email" 
                                placeholder="Email" 
                                className="pl-10"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                disabled={loading}
                                required
                            />
                        </div>
                    </CardContent>
                    <CardFooter className="flex flex-col gap-4">
                        <Button 
                            className="w-full"
                            onClick={handleResetPassword}
                            disabled={loading}
                            type="button"
                        >
                            {loading ? (
                                <>
                                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                    Sending...
                                </>
                            ) : (
                                "Send Reset Link"
                            )}
                        </Button>
                        <div className="text-center text-sm">
                            <p>
                                Remember your password?{" "}
                                <Link to="/login" className="text-blue-600 hover:underline">
                                    Sign In
                                </Link>
                            </p>
                        </div>
                    </CardFooter>
                </Card>
            </div>
        </div>
    );
}
