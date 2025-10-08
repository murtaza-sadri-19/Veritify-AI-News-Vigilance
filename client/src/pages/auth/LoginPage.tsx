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
import { Mail, Lock, Loader2 } from "lucide-react";
import { Link, useNavigate } from "react-router-dom";
import { useState } from "react";
import { useAuth } from "@/contexts/AuthContext";
import toast from "react-hot-toast";

export function LoginPage() {
    const navigate = useNavigate();
    const { login, loginWithGoogle } = useAuth();
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");

    const handleLogin = async (e: React.FormEvent) => {
        e.preventDefault();
        
        // Validation
        if (!email || !password) {
            setError("Please fill in all fields");
            toast.error("Please fill in all fields");
            return;
        }

        try {
            setError("");
            setLoading(true);
            await login(email, password);
            toast.success("Login successful!");
            navigate("/dashboard");
        } catch (err: any) {
            console.error("Login error:", err);
            let errorMessage = "Failed to login";
            
            // Handle specific Firebase error codes
            if (err.code === "auth/user-not-found") {
                errorMessage = "No account found with this email";
            } else if (err.code === "auth/wrong-password") {
                errorMessage = "Incorrect password";
            } else if (err.code === "auth/invalid-email") {
                errorMessage = "Invalid email address";
            } else if (err.code === "auth/user-disabled") {
                errorMessage = "This account has been disabled";
            } else if (err.code === "auth/too-many-requests") {
                errorMessage = "Too many failed attempts. Please try again later";
            }
            
            setError(errorMessage);
            toast.error(errorMessage);
        } finally {
            setLoading(false);
        }
    };

    const handleGoogleLogin = async () => {
        try {
            setError("");
            setLoading(true);
            await loginWithGoogle();
            toast.success("Login successful!");
            navigate("/dashboard");
        } catch (err: any) {
            console.error("Google login error:", err);
            let errorMessage = "Failed to login with Google";
            
            if (err.code === "auth/popup-closed-by-user") {
                errorMessage = "Login cancelled";
            } else if (err.code === "auth/popup-blocked") {
                errorMessage = "Popup blocked. Please allow popups for this site";
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
                        <CardTitle className="text-2xl">Sign In</CardTitle>
                        <CardDescription>
                            Enter your credentials to access your account.
                        </CardDescription>
                        {error && (
                            <div className="text-sm text-red-600 mt-2 p-2 bg-red-50 rounded">
                                {error}
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
                        <div className="relative">
                            <Lock className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
                            <Input
                                type="password"
                                placeholder="Password"
                                className="pl-10"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                disabled={loading}
                                required
                                onKeyPress={(e) => {
                                    if (e.key === 'Enter') {
                                        handleLogin(e);
                                    }
                                }}
                            />
                        </div>
                    </CardContent>
                    <CardFooter className="flex flex-col gap-4">
                        <Button 
                            className="w-full" 
                            onClick={handleLogin} 
                            type="button"
                            disabled={loading}
                        >
                            {loading ? (
                                <>
                                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                    Signing in...
                                </>
                            ) : (
                                "Sign In"
                            )}
                        </Button>
                        <Button 
                            variant="outline" 
                            className="w-full" 
                            onClick={handleGoogleLogin} 
                            type="button"
                            disabled={loading}
                        >
                            {loading ? (
                                <>
                                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                    Connecting...
                                </>
                            ) : (
                                "Sign in with Google"
                            )}
                        </Button>
                        <div className="text-center text-sm">
                            <p>
                                Don't have an account?{" "}
                                <Link to="/signup" className="text-blue-600 hover:underline">
                                    Sign Up
                                </Link>
                            </p>
                            <p>
                                <Link
                                    to="/forgot-password"
                                    className="text-blue-600 hover:underline"
                                >
                                    Forgot Password?
                                </Link>
                            </p>
                        </div>
                    </CardFooter>
                </Card>
            </div>
        </div>
    );
}
