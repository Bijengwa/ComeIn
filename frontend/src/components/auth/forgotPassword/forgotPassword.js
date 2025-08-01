import React, { useState } from 'react';
import './forgotPassword.css';

export default function ForgotPassword() {
    const [useEmail, setUseEmail] = useState(true);
    const [inputValue, setInputValue] = useState("");

    const toggleMethod = () => {
        setUseEmail(!useEmail);
        setInputValue("");
    };

    const handleResend = () => {
        if (useEmail) {
            alert("Resending email...");
        } else {
            alert("Resending SMS...");
        }
    };

    const handleSubmit = (e) => {
        e.preventDefault();
        if(useEmail){
            console.log("Sending reset link to email:", inputValue);
        } else {
            console.log("Sending reset code to phone:", inputValue);
        }
    };

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
                </form>
            </div>
        </div>
    );
    
}