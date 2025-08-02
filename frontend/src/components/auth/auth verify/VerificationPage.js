import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

import './verification.css';

export default function VerificationPage() {
    const [phone, setPhone] = useState('');
    const [phoneCode, setPhoneCode] = useState('');
    const [email, setEmail] = useState('');
    const [emailCode, setEmailCode] = useState('');
    const [canEditPhone, setCanEditPhone] = useState(false);
    const [canEditEmail, setCanEditEmail] = useState(false);
    const [success, setSuccess] = useState('');
    const [error, setError] = useState('');
    const [phoneTimer, setPhoneTimer] = useState(0);
    const [emailTimer, setEmailTimer] = useState(0);
    const [isPhoneVerified, setIsPhoneVerified] = useState(false);
    const [isEmailVerified, setIsEmailVerified] = useState(false);
    const navigate = useNavigate();

    // Countdown effects
    useEffect(() => {
        if (phoneTimer > 0) {
            const interval = setInterval(() => setPhoneTimer(prev => prev - 1), 1000);
            return () => clearInterval(interval);
        }
    }, [phoneTimer]);

    useEffect(() => {
        if (emailTimer > 0) {
            const interval = setInterval(() => setEmailTimer(prev => prev - 1), 1000);
            return () => clearInterval(interval);
        }
    }, [emailTimer]);

    useEffect(() => {
    const storedEmail = localStorage.getItem("verify_email");
    const storedPhone = localStorage.getItem("verify_phone");

    if (storedEmail) setEmail(storedEmail);
    if (storedPhone) setPhone(storedPhone);
    }, []);

    const handleVerify = async (type) => {
        try {
            const response = await fetch('/api/auth/verify', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    code: type === 'phone' ? phoneCode : emailCode,
                    target: type
                }),
            });

            const data = await response.json();

            if (response.ok) {
                setSuccess(data.message);
                setError('');

                if (type === 'phone') {
                    localStorage.removeItem('verify_phone');
                }
                if (type === 'email') {
                    localStorage.removeItem('verify_email');
                }

            } else {
                setError(data.error);
                setSuccess('');
            }
        } catch (err) {
            setError('Verification failed. Please try again.');
            setSuccess('');
        }
    };

    const handleResendCode = async (type) => {
        try {
            let endpoint = '';
            let payload = {};

            if (type === 'phone') {
                endpoint = '/api/auth/send-phone-otp/';
                payload = { phone_number: phone };
                setPhoneTimer(30);
            } else if (type === 'email') {
                endpoint = '/api/auth/resend-verification/';
                payload = { email: email };
                setEmailTimer(30);
            }

            const response = await fetch(endpoint, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload),
            });

            const data = await response.json();

            if (response.ok) {
                setSuccess(data.message || 'Code resent successfully.');
                setError('');
            } else {
                setError(data.error || 'Resend failed.');
                setSuccess('');
            }
        } catch (err) {
            setError('Resend failed. Please try again.');
            setSuccess('');
        }
    };

    useEffect(() => {
        if (isPhoneVerified && isEmailVerified) {
            setTimeout(() => {
                navigate('/dashboard');
            }, 1500)
        }
    }, [isPhoneVerified, isEmailVerified, navigate]);

    return (
        <div className='verify-container'>
            <h2>Verify Your Account</h2>

            <div className='verify-credential'>
                <h2>Phone Number</h2>

                <div className='verifying'>
                    <div className='credential' >
                        <input
                            type='text'
                            placeholder={canEditPhone ? "Edit phone number" : "Phone number used in registration"}
                            value={phone}
                            disabled={!canEditPhone}
                            onChange={(e) => setPhone(e.target.value)}
                            className={!canEditPhone ? 'disabled' : ''}
                        />
                        <button onClick={() => setCanEditPhone(true)}>Edit Phone</button>
                    </div>

                    <div className='code-box'>
                        <input
                            type='text'
                            placeholder='Enter verification code'
                            value={phoneCode}
                            onChange={(e) => setPhoneCode(e.target.value)}
                        />
                        <button
                            className='resend-btn'
                            onClick={() => handleResendCode('phone')}
                            disabled={!canEditPhone || phoneTimer > 0}
                        >
                            {phoneTimer > 0 ? `Wait ${phoneTimer}s` : 'Resend Code'}
                        </button>
                    </div>
                    <button onClick={() => handleVerify('phone')}>Verify Phone</button>
                </div>
            </div>

            <div className='verify-credential'>
                <h2>Email</h2>
                <div className='verifying'>
                    <div className='credential'>
                    <input
                        type='text'
                        placeholder={canEditEmail ? "Edit email address" : "Email used in registration"}
                        value={email}
                        disabled={!canEditEmail}
                        onChange={(e) => setEmail(e.target.value)}
                        className={!canEditEmail ? 'disabled' : ''}
                    />
                    <button onClick={() => setCanEditEmail(true)}>Edit Email</button>

                    </div>

                    <div className='code-box'>
                        <input
                            type='text'
                            placeholder='Enter verification code'
                            value={emailCode}
                            onChange={(e) => setEmailCode(e.target.value)}
                        />
                        <button
                            className='resend-btn'
                            onClick={() => handleResendCode('email')}
                            disabled={!canEditEmail || emailTimer > 0}
                        >
                            {emailTimer > 0 ? `Wait ${emailTimer}s` : 'Resend Code'}
                        </button>
                    </div>
                    <button onClick={() => handleVerify('email')}>Verify Email</button>
                </div>
            </div>

            {error && <p className='error-msg'>{error}</p>}
            {success && <p className='success-msg'>{success}</p>}
        </div>
    );
}
