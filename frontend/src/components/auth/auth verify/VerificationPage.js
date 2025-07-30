import React, { useState } from 'react';
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
            } else {
                setError(data.error);
                setSuccess('');
            }
        } catch (err) {
            setError('Verification failed. Please try again.');
            setSuccess('');
        }
    };

    return (
        <div className='verify-container'>
            <h2>Verify Your Account</h2>

            <div className='verify-credential'>
                <h2>Phone Number</h2>
                <div className='verifying'>
                    <input
                        type='text'
                        placeholder='Enter phone number'
                        value={phone}
                        disabled={!canEditPhone}
                        onChange={(e) => setPhone(e.target.value)}
                        className={!canEditPhone ? 'disabled' : ''}
                    />
                    <button onClick={() => setCanEditPhone(true)}>Edit Phone</button>
                    <input
                        type='text'
                        placeholder='Enter verification code'
                        value={phoneCode}
                        onChange={(e) => setPhoneCode(e.target.value)}
                    />
                    <button onClick={() => handleVerify('phone')}>Verify Phone</button>
                </div>
            </div>

            <div className='verify-credential'>
                <h2>Email</h2>
                <div className='verifying'>
                    <input
                        type='text'
                        placeholder='Edit email address'
                        value={email}
                        disabled={!canEditEmail}
                        onChange={(e) => setEmail(e.target.value)}
                        className={!canEditEmail ? 'disabled' : ''}
                    />
                    <button onClick={() => setCanEditEmail(true)}>Edit Email</button>
                    <input
                        type='text'
                        placeholder='Enter verification code'
                        value={emailCode}
                        onChange={(e) => setEmailCode(e.target.value)}
                    />
                    <button onClick={() => handleVerify('email')}>Verify Email</button>
                </div>
            </div>

            {error && <p className='error'>{error}</p>}
            {success && <p className='success'>{success}</p>}
        </div>
    );
}
