import React, { use, useEffect, useState } from 'react';
import './forgotPassword.css';

export default function ForgotPassword() {
    const [useEmail, setUseEmail] = useState(true);
    const [inputValue, setInputValue] = useState("");
    const [timer, setTimer] = useState(0);
    const [success, setSuccess] = useState("");
    const [error, setError] = useState("");

    const toggleMethod = () => {
        setUseEmail(!useEmail);
        setInputValue("");
    };

    const handleResend = () => {
        if (timer > 0) return;
        setTimer(30);
        setSuccess(useEmail ? "Email resent" : "SMS resent");
        setError("");
    };

    const handleSubmit = (e) => {
        e.preventDefault();
        if(useEmail){
            console.log("Sending reset link to email:", inputValue);
        } else {
            console.log("Sending reset code to phone:", inputValue);
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
                <p>
                    {useEmail 
                        ? "Please enter your email to reset your password."
                        : "Please enter your phone number to reset your password."}
                </p>

                <button className='choice-btn' onClick={toggleMethod}>
                    {useEmail ? "Use Phone Number" : "Use Email"}
                </button>
                <form onSubmit={handleSubmit}>
                    <input 
                        type={useEmail ? "Email" : "tel"}
                        placeholder={useEmail ? "Email" : "Phone Number"}
                        value={inputValue}
                        onChange={(e) => setInputValue(e.target.value)}
                        required
                    />

                    <button type='submit'>Send</button>

                    <button 
                        type='button'
                        className='resend-btn'
                        onClick={handleResend}
                    >
                        {useEmail ? "Resend Email" : "Resend SMS"}
                    </button>

                    {error && <p className='error-message'>{error}</p>}
                    {success && <p className='success-message'>{success}</p>}
                    
                </form>
            </div>
        </div>
    );
    
}