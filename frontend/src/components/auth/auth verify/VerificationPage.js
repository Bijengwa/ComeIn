// VerificationPage.jsx
import React, { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import './verification.css';

const API = 'http://127.0.0.1:8000';
const RESEND_PHONE_OTP = `${API}/api/auth/resend-phone-otp/`;   // ensure this exists on backend
const RESEND_EMAIL     = `${API}/api/auth/resend-verification/`;
const VERIFY_PHONE     = `${API}/api/auth/verify-phone`;

// ✅ put this OUTSIDE any other function
function openInbox(email) {
  const domain = (email.split('@')[1] || '').toLowerCase();
  const INBOX = {
    'gmail.com': 'https://mail.google.com/mail/u/0/#inbox',
    'googlemail.com': 'https://mail.google.com/mail/u/0/#inbox',
    'outlook.com': 'https://outlook.live.com/mail/0/inbox',
    'hotmail.com': 'https://outlook.live.com/mail/0/inbox',
    'live.com': 'https://outlook.live.com/mail/0/inbox',
    'msn.com': 'https://outlook.live.com/mail/0/inbox',
    'office.com': 'https://outlook.office.com/mail/',
    'office365.com': 'https://outlook.office.com/mail/',
    'microsoft.com': 'https://outlook.office.com/mail/',
    'yahoo.com': 'https://mail.yahoo.com/',
    'ymail.com': 'https://mail.yahoo.com/',
    'rocketmail.com': 'https://mail.yahoo.com/',
    'icloud.com': 'https://www.icloud.com/mail',
    'me.com': 'https://www.icloud.com/mail',
    'mac.com': 'https://www.icloud.com/mail',
    'proton.me': 'https://mail.proton.me/u/0/inbox',
    'protonmail.com': 'https://mail.proton.me/u/0/inbox',
    'zoho.com': 'https://mail.zoho.com/zm/#mail/inbox',
    'gmx.com': 'https://navigator.gmx.com/mail',
    'mail.com': 'https://www.mail.com/int/#.1258-header-mailcom',
    'aol.com': 'https://mail.aol.com/',
    'yandex.com': 'https://mail.yandex.com/'
  };

  let url = INBOX[domain];
  if (!url) {
    if (domain.endsWith('.edu') || domain.endsWith('.ac.tz') ||
        domain.includes('outlook') || domain.includes('office')) {
      url = 'https://outlook.office.com/mail/';
    } else if (domain.includes('gmail') || domain.includes('google')) {
      url = 'https://mail.google.com/mail/u/0/#inbox';
    } else {
      url = `https://${domain}`;
    }
  }
  window.open(url, '_blank', 'noopener,noreferrer');
}

export default function VerificationPage() {
  const [phone, setPhone] = useState('');
  const [phoneCode, setPhoneCode] = useState('');
  const [email, setEmail] = useState('');
  const [canEditPhone, setCanEditPhone] = useState(false);
  const [canEditEmail, setCanEditEmail] = useState(false);
  const [success, setSuccess] = useState('');
  const [error, setError] = useState('');
  const [phoneTimer, setPhoneTimer] = useState(0);
  const [emailTimer, setEmailTimer] = useState(0);
  const [isPhoneVerified, setIsPhoneVerified] = useState(false);
  const [isEmailVerified, setIsEmailVerified] = useState(false);

  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    const storedEmail = localStorage.getItem('verify_email');
    const storedPhone = localStorage.getItem('verify_phone');
    if (storedEmail) setEmail(storedEmail);
    if (storedPhone) setPhone(storedPhone);
  }, []);

  useEffect(() => {
    if (location.state?.message) setSuccess(location.state.message);
    if (location.state?.error) setError(location.state.error);
    if (typeof location.state?.emailVerified === 'boolean') {
      setIsEmailVerified(location.state.emailVerified);
    }
    window.history.replaceState({}, document.title);
  }, [location.state]);

  useEffect(() => {
    if (phoneTimer > 0) {
      const t = setInterval(() => setPhoneTimer(p => p - 1), 1000);
      return () => clearInterval(t);
    }
  }, [phoneTimer]);

  useEffect(() => {
    if (emailTimer > 0) {
      const t = setInterval(() => setEmailTimer(p => p - 1), 1000);
      return () => clearInterval(t);
    }
  }, [emailTimer]);

  const handleVerifyPhone = async () => {
    setSuccess(''); setError('');
    try {
      const res = await fetch(VERIFY_PHONE, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ phone_number: phone, otp: phoneCode })
      });
      const data = await res.json();
      if (res.ok) {
        setIsPhoneVerified(true);
        localStorage.removeItem('verify_phone');
        setSuccess(data.message || 'Phone number verified!');
        setCanEditPhone(false);
      } else {
        setError(data.error || 'Invalid or expired OTP.');
      }
    } catch {
      setError('Verification failed. Please try again.');
    }
  };

  const handleResend = async (type) => {
    setSuccess(''); setError('');
    try {
      const endpoint = type === 'email' ? RESEND_EMAIL : RESEND_PHONE_OTP;
      const payload  = type === 'email' ? { email } : { phone_number: phone };
      const res = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      const data = await res.json();
      if (res.ok) {
        setSuccess(data.message || 'Code sent successfully.');
        if (type === 'email') setEmailTimer(30);
        else setPhoneTimer(30);
      } else {
        setError(data.error || 'Sending failed.');
      }
    } catch {
      setError('Sending failed. Please try again.');
    } finally {
      setTimeout(() => { setError(''); setSuccess(''); }, 5000);
    }
  };

  useEffect(() => {
    if (isPhoneVerified && isEmailVerified) {
      setTimeout(() => navigate('/'), 1200);
    }
  }, [isPhoneVerified, isEmailVerified, navigate]);

  return (
    <div className="verify-container">
      <h2>Verify Your Account</h2>

      {/* PHONE */}
      <div className="verify-credential">
        <h2>Phone Number {isPhoneVerified ? '✅' : ''}</h2>
        <div className="verifying">
          <div className="credential">
            <input
              type="text"
              placeholder={canEditPhone ? 'Edit phone number' : 'Phone number used in registration'}
              value={phone}
              disabled={!canEditPhone || isPhoneVerified}
              onChange={(e) => setPhone(e.target.value)}
              className={!canEditPhone || isPhoneVerified ? 'disabled' : ''}
            />
            <button disabled={isPhoneVerified} onClick={() => setCanEditPhone(true)}>Edit Phone</button>
          </div>
          <div className="code-box">
            <input
              type="text"
              placeholder="Enter verification code"
              value={phoneCode}
              disabled={isPhoneVerified}
              onChange={(e) => setPhoneCode(e.target.value)}
            />
            <button
              className="resend-btn"
              onClick={() => handleResend('phone')}
              disabled={isPhoneVerified || !phone || phoneTimer > 0}
            >
              {phoneTimer > 0 ? `Wait ${phoneTimer}s` : 'Resend Code'}
            </button>
          </div>
          <button disabled={isPhoneVerified || !phone || !phoneCode} onClick={handleVerifyPhone}>
            Verify Phone
          </button>
        </div>
      </div>

      {/* EMAIL */}
      <div className="verify-credential">
        <h2>Email {isEmailVerified ? '✅' : ''}</h2>
        <div className="verifying">
          <div className="credential">
            <input
              type="email"
              placeholder={canEditEmail ? 'Edit email address' : 'Email used in registration'}
              value={email}
              disabled={!canEditEmail || isEmailVerified}
              onChange={(e) => setEmail(e.target.value)}
              className={!canEditEmail || isEmailVerified ? 'disabled' : ''}
            />
            <button disabled={isEmailVerified} onClick={() => setCanEditEmail(true)}>Edit Email</button>
          </div>
          <div className="code-box">
            <input type="text" value="Check your inbox for the link" disabled className="disabled" />
            <button
              className="resend-btn"
              onClick={() => handleResend('email')}
              disabled={isEmailVerified || !email || emailTimer > 0}
            >
              {emailTimer > 0 ? `Wait ${emailTimer}s` : 'Resend Email Link'}
            </button>
          </div>
          <button onClick={() => openInbox(email)} disabled={isEmailVerified} title="Open your inbox">
            Open Inbox
          </button>
        </div>
      </div>

      {error && <p className="error-msg">{error}</p>}
      {success && <p className="success-msg">{success}</p>}
    </div>
  );
}
