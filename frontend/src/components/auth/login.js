import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { FaEye, FaEyeSlash } from "react-icons/fa";

import "./login.css";

export default function Login() {
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [showPassword, setShowPassword] = useState(false);
    const [error, setError] = useState("");
    const [success, setSuccess] = useState("");
    const navigate = useNavigate();
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);

        try {
            const response = await fetch("http://127.0.0.1:8000/api/auth/login/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ email, password })
            });

            const data = await response.json();

            if (response.ok) {
                setSuccess("Login successful!");
                setError("");

                // Save JWT tokens and user info
                localStorage.setItem("accessToken", data.access);
                localStorage.setItem("refreshToken", data.refresh);
                localStorage.setItem("userFullName", data.user.full_name); 

                navigate("/dashboard");
            } else {
                setError(data.error || "Invalid credentials"); 
                setSuccess("");
            }
        } catch (err) {
            setError("Login failed. Please try again.");
            setSuccess("");
        } finally {
            setLoading(false);
        }
    };

    const handleForgotPassword = () => {
        navigate("/forgot-password");
    };

    return (
        <div className="login-container">
            <h1 className="logo">ComeIn Login</h1>

            <div className="login-card">
                <h2>Login</h2>

                {error && <p className="error-message">{error}</p>}
                {success && <p className="success-message">{success}</p>}

                <form onSubmit={handleSubmit}>
                    <input
                        type="email"
                        className="login-input"
                        placeholder="Email"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        required
                    />

                    <div className="password-field">
                        <input
                            type={showPassword ? "text" : "password"}
                            className="login-input"
                            placeholder="Password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            required
                        />
                        <span
                            className="toggle-icon"
                            onClick={() => setShowPassword(!showPassword)}
                        >
                            {showPassword ? <FaEyeSlash /> : <FaEye />}
                        </span>
                        <button type="button" className="forgot-password-btn" onClick={handleForgotPassword}>
                            Forgot Password?
                        </button>
                    </div>

                    <button type="submit" className="login-btn" disabled={loading}>{loading ? "Loading..." : "Submit"}</button>
                    {loading && <p className="loading-message">Logging in...</p>}
                </form>

                <button className="google-btn">
                    <img
                        src="https://www.svgrepo.com/show/355037/google.svg"
                        alt="google"
                    /> Sign in with Google
                </button>

                <p className="register-link">
                    Don&apos;t have an account? <a href="/register">Register</a>
                </p>
            </div>
        </div>
    );
}
