import React, { useState, useEffect } from "react";
import './ResetPassword.css';

export default function ResetPassword() {
    const [password, setPassword] = useState("");
    const [confirmPassword, setConfirmPassword] = useState("");
    const [showPassword, setShowPassword] = useState(false);
    const [showConfirm, setShowConfirm] = useState(false);
    const [error, setError] = useState("");
    const [success, setSuccess] = useState(false);

    useEffect(() => {
        if (confirmPassword && password !== confirmPassword) {
            setError("Passwords do not match");
            setSuccess("");
        } else {
            setError("");
        }
    }, [password, confirmPassword]);

    const handleSubmit = (e) => {
        e.preventDefault();

        if (password.length < 6) {
            setError("Password must be at least 6 characters long");
            setSuccess("");
            return;
        }

        if (password !== confirmPassword) {
            setError("Passwords do not match");
            setSuccess("");
            return;
        }

        setSuccess("✅Password reset successfully!");
        setError("");
        setPassword("");
        setConfirmPassword("");
    };

    return (
        <div className="reset-password-container">
            <h2>Reset Your Password</h2>

            {error && <p className="error-message">{error}</p>}
            {success && <p className="success-message">{success}</p>}

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
                    > {showConfirm ? '🙈' : '👁️'} </span>
                </div>

                <button type="submit" className="reset-button">
                    Reset Password 
                </button>
            </form>
        </div>

    )
}