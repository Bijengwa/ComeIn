import React, { useState } from "react";
import "./login.css";

export default function Login() {
    const [showPassword, setShowPassword] = useState(false);

    return (
        <div className="login-container">
            <h1 className="logo">ComeIn Login</h1>

            <div className="login-card">
                <h2>Login</h2>

                <form>
                    <input type="email" className="login-input" placeholder="Email" required />

                    <div className="password-field">
                        <input 
                            type={showPassword ? "text" : "password"} 
                            className="login-input" 
                            placeholder="Password" 
                            required 
                        />
                        <span 
                            className="toggle-icon" 
                            onClick={() => setShowPassword(!showPassword)}>
                            {showPassword ? "🙈" : "👁️"}
                        </span>
                    </div>

                    <button type="submit" className="login-btn">Login</button>
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
