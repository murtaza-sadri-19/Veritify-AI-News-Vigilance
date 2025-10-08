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
import { Mail, Lock, User, Loader2 } from "lucide-react";
import { Link, useNavigate } from "react-router-dom";
import { useState } from "react";
import { useAuth } from "@/contexts/AuthContext";
import toast from "react-hot-toast";

export function SignupPage() {
    const navigate = useNavigate();
    const { signup, signupWithGoogle } = useAuth();
    const [name, setName] = useState("");
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [confirmPassword, setConfirmPassword] = useState("");
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");

    const handleSignup = async (e: React.FormEvent) => {
        e.preventDefault();
        
        // Validation
        if (!name || !email || !password || !confirmPassword) {
            setError("Please fill in all fields");
            toast.error("Please fill in all fields");
            return;
        }

        if (password.length < 6) {
            setError("Password must be at least 6 characters");
            toast.error("Password must be at least 6 characters");
            return;
        }

        if (password !== confirmPassword) {
            setError("Passwords do not match");
            toast.error("Passwords do not match");
            return;
        }

        try {
            setError("");
            setLoading(true);
            await signup(email, password, name);
            toast.success("Account created successfully!");
            navigate("/dashboard");
        } catch (err: any) {
            console.error("Signup error:", err);
            let errorMessage = "Failed to create account";
            
            // Handle specific Firebase error codes
            if (err.code === "auth/email-already-in-use") {
                errorMessage = "An account with this email already exists";
            } else if (err.code === "auth/invalid-email") {
                errorMessage = "Invalid email address";
            } else if (err.code === "auth/weak-password") {
                errorMessage = "Password is too weak";
            } else if (err.code === "auth/operation-not-allowed") {
                errorMessage = "Email/password accounts are not enabled";
            }
            
            setError(errorMessage);
            toast.error(errorMessage);
        } finally {
            setLoading(false);
        }
    };

    const handleGoogleSignup = async () => {
        try {
            setError("");
            setLoading(true);
            await signupWithGoogle();
            toast.success("Account created successfully!");
            navigate("/dashboard");
        } catch (err: any) {
            console.error("Google signup error:", err);
            let errorMessage = "Failed to sign up with Google";
            
            if (err.code === "auth/popup-closed-by-user") {
                errorMessage = "Sign up cancelled";
            } else if (err.code === "auth/popup-blocked") {
                errorMessage = "Popup blocked. Please allow popups for this site";
            } else if (err.code === "auth/account-exists-with-different-credential") {
                errorMessage = "An account already exists with this email";
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
                        <CardTitle className="text-2xl">Create an Account</CardTitle>
                        <CardDescription>
                            Fill in the details below to get started.
                        </CardDescription>
                        {error && (
                            <div className="text-sm text-red-600 mt-2 p-2 bg-red-50 rounded">
                                {error}
                            </div>
                        )}
                    </CardHeader>
                    <CardContent className="space-y-4">
                        <div className="relative">
                            <User className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
                            <Input
                                type="text"
                                placeholder="Full Name"
                                className="pl-10"
                                value={name}
                                onChange={(e) => setName(e.target.value)}
                                disabled={loading}
                                required
                            />
                        </div>
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
                                placeholder="Password (min 6 characters)"
                                className="pl-10"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                disabled={loading}
                                required
                                minLength={6}
                            />
                        </div>
                        <div className="relative">
                            <Lock className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
                            <Input
                                type="password"
                                placeholder="Confirm Password"
                                className="pl-10"
                                value={confirmPassword}
                                onChange={(e) => setConfirmPassword(e.target.value)}
                                disabled={loading}
                                required
                            />
                        </div>
                    </CardContent>
                    <CardFooter className="flex flex-col gap-4">
                        <Button 
                            className="w-full" 
                            onClick={handleSignup} 
                            type="button"
                            disabled={loading}
                        >
                            {loading ? (
                                <>
                                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                    Creating account...
                                </>
                            ) : (
                                "Sign Up"
                            )}
                        </Button>
                        <Button 
                            variant="outline" 
                            className="w-full" 
                            onClick={handleGoogleSignup} 
                            type="button"
                            disabled={loading}
                        >
                            {loading ? (
                                <>
                                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                    Connecting...
                                </>
                            ) : (
                                "Sign up with Google"
                            )}
                        </Button>
                        <div className="text-center text-sm">
                            <p>
                                Already have an account?{" "}
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
