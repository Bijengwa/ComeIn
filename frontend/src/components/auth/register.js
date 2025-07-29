import React, { useState } from 'react';
import './register.css'; 

export default function Register() {
    const [showPassword, setShowPassword] = useState(false);
    const [showConfirmPassword, setShowConfirmPassword] = useState(false);

    return (
        <div className='register-container' >

            <div className='register-card'>
                <h2>ComeIn Register</h2>

                <form className='register-form'>

                    <input type='text' className='register-input' placeholder='Username' required />
                    <input type='email' className='register-input' placeholder='Email' required />

                    <div className='password-field'>
                        <input type={showPassword ? 'text' : 'password'} className='register-input' placeholder='Password' required />
                        <span
                            className='toggle-icon'
                            onClick={() => setShowPassword(!showPassword)}
                        >
                            {showPassword ? '🙈' : '👁️'}
                        </span>
                    </div>

                    <div className='password-field'>
                        <input type={showConfirmPassword ? 'text' : 'password'} className='register-input' placeholder='Confirm Password' required />
                        <span className='toggle-icon' onClick={() => setShowConfirmPassword(!showConfirmPassword)}>
                            {showConfirmPassword ? '🙈' : '👁️'}
                        </span>
                    </div>
                    <button type='submit' className='register-btn'>Register</button>

                </form>

                <button className='google-btn'>
                    <img
                        src="https://www.svgrepo.com/show/355037/google.svg"
                        alt="google"
                    /> Sign up with Google
                </button>

                <p className='login-link'>
                    Already have an account? <a href="/login">Login</a>
                </p>

            </div>
        </div>
    );
}