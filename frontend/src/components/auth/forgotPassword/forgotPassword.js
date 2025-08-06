import React, { useEffect, useState } from 'react';
import './forgotPassword.css';

export default function ForgotPassword() {
    const [useEmail, setUseEmail] = useState(true);
    const [inputValue, setInputValue] = useState("");
    const [timer, setTimer] = useState(0);
    const [success, setSuccess] = useState("");
    const [error, setError] = useState("");
    const [loading, setLoading] = useState(false);

    const toggleMethod = () => {
        setUseEmail(!useEmail);
        setInputValue("");
        setSuccess("");
        setError("");
    };

    const handleResend = () => {
        if (timer > 0) return;
        setTimer(30);
        setSuccess(useEmail ? "✅ Email has been resent" : "✅ SMS has been resent");
        setError("");
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setSuccess("");
        setError("");

        try {
            const response = await fetch("http://127.0.0.1:8000/api/auth/forgot-password/", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    [useEmail ? "email" : "phone"]: inputValue
                })
            });

            const data = await response.json();

            if (!response.ok) {
                if (data.detail === "Email not found" || data.detail === "Phone number not found") {
                    setError(`❌ ${data.detail}`);
                } else {
                    setError("❌ An unexpected error occurred. Please try again.");
                }
            } else {
                setSuccess("✅ Reset link/code sent successfully!");
            }
        } catch (err) {
            setError("⚠️ Cannot connect to server. Please check your internet or try again later.");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        if (timer > 0) {
            const countdown = setInterval(() => setTimer(prev => prev - 1), 1000);
            return () => clearInterval(countdown);
        }
    }, [timer]);

    return (
        <div className='forgot-password-container'>
            <div className='forgot-password-card'>
                <h2>Forgot Password</h2>
                <p>{useEmail ? "Please enter your email to reset your password." : "Please enter your phone number to reset your password."}</p>

                <button className='choice-btn' onClick={toggleMethod}>
                    {useEmail ? "Use Phone Number" : "Use Email"}
                </button>

                <form onSubmit={handleSubmit}>
                    <input
                        type={useEmail ? "email" : "tel"}
                        placeholder={useEmail ? "Email" : "Phone Number"}
                        value={inputValue}
                        onChange={(e) => setInputValue(e.target.value)}
                        required
                    />

                    <button type='submit' disabled={loading}>
                        {loading ? "Sending..." : "Send"}
                    </button>

                    <button
                        type='button'
                        className='resend-btn'
                        onClick={handleResend}
                        disabled={timer > 0}
                    >
                        {timer > 0 ? `Wait ${timer}s` : useEmail ? "Resend Email" : "Resend SMS"}
                    </button>

                    {error && <p className='error-message'>{error}</p>}
                    {success && <p className='success-message'>{success}</p>}
                </form>
            </div>
        </div>
    );
}
