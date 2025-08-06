import React, { useState } from "react";
import "./AdminLogin.css";

export default function AdminLogin() {
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");
    const [success, setSuccess] = useState("");

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError("");
        setSuccess("");
        setLoading(true);

        try {
            const response = await fetch("http://127.0.0.1:8000/api/admin/login//", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ email, password }),
            });

            const data = await response.json();

            if (response.ok) {
                setSuccess("✅ Login successful!");
                localStorage.setItem("adminAccessToken", data.access);
                localStorage.setItem("adminRefreshToken", data.refresh);
                window.location.href = "/admin/dashboard";
            } else {
                setError(`❌ ${data.detail || "Login failed. Please try again."}`);
            }
        } catch (err) {
            setError("⚠️ Cannot connect to server. Please check your internet or try again later.");
        } finally {
            setLoading(false);
        }
    }

    return (
        <form className="container" onSubmit={handleSubmit}>
            <h2>Admin Login</h2>

            <div className="admin" >
                <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="Enter the email" required />
                <input type="password" placeholder="Admin Password" onChange={(e) => setPassword(e.target.value)} required />

                <button type="submit" disabled={loading} >{loading ? "Loading ..." : "ENTER"}</button>
            </div>

            {error && <p className="error-msg">{error}</p>}
            {success && <p className="success-msg">{success}</p>}
        </form>
    );
}