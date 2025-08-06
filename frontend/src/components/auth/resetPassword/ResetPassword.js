import React, { useState, useEffect } from "react";
import { useLocation } from "react-router-dom";
import './ResetPassword.css';

export default function ResetPassword() {
    const [password, setPassword] = useState("");
    const [confirmPassword, setConfirmPassword] = useState("");
    const [showPassword, setShowPassword] = useState(false);
    const [showConfirm, setShowConfirm] = useState(false);
    const [error, setError] = useState("");
    const [success, setSuccess] = useState("");
    const [loading, setLoading] = useState(false);

    const location = useLocation();
    const queryParams = new URLSearchParams(location.search);
    const token = queryParams.get("token");

    useEffect(() => {
        if (confirmPassword && password !== confirmPassword) {
            setError("❌ Passwords do not match");
            setSuccess("");
        } else {
            setError("");
        }
    }, [password, confirmPassword]);

    const handleSubmit = async (e) => {
        e.preventDefault();

        if (password.length < 6) {
            setError("❌ Password must be at least 6 characters long");
            setSuccess("");
            return;
        }

        if (password !== confirmPassword) {
            setError("❌ Passwords do not match");
            setSuccess("");
            return;
        }

        setLoading(true);
        setError("");
        setSuccess("");

        try {
            const response = await fetch("http://127.0.0.1:8000/api/auth/reset-password-confirm/", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ token, password })
            });

            const data = await response.json();

            if (response.ok) {
                setSuccess("✅ Password reset successfully!");
                setPassword("");
                setConfirmPassword("");
            } else {
                setError(`❌ ${data.detail || "Something went wrong. Try again."}`);
            }
        } catch (err) {
            setError("⚠️ Unable to connect to server. Please try again later.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="reset-password-container">
            <h2>Reset Your Password</h2>

            {error && <p className="error-message">{error}</p>}
            {success && <p className="success-message">{success}</p>}
            {loading && <p className="loading-message">⏳ Processing...</p>}

            <form onSubmit={handleSubmit}>
                <div className="password-field">
                    <input 
                        type={showPassword ? "text" : "password"}
                        placeholder="New Password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        required
                    />
                    <span
                        onClick={() => setShowPassword(!showPassword)}
                        className="toggle-password"
                    >
                        {showPassword ? "🙈" : "👁️"}
                    </span>
                </div>

                <div className="password-field">
                    <input 
                        type={showConfirm ? "text" : "password"}
                        placeholder="Confirm Password"
                        value={confirmPassword}
                        onChange={(e) => setConfirmPassword(e.target.value)}
                        required
                    />
                    <span 
                        onClick={() => setShowConfirm(!showConfirm)}
                        className="toggle-password"
                    >
                        {showConfirm ? '🙈' : '👁️'}
                    </span>
                </div>

                <button type="submit" className="reset-button" disabled={loading}>
                    {loading ? "Resetting..." : "Reset Password"}
                </button>
            </form>
        </div>
    );
}
