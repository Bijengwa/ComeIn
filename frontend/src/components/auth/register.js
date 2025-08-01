import React, { useState } from "react";
import "./register.css";

export default function Register() {
  const [fullname, setFullname] = useState("");
  const [email, setEmail] = useState("");
  const [phone, setPhone] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (password !== confirmPassword) {
      setError("Passwords do not match");
      setSuccess("");
      return;
    }

    try {
      const response = await fetch("http://127.0.0.1:8000/api/auth/register/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          full_name: fullname,
          email: email,
          phone_number: phone,
          password: password,
          confirm_password: confirmPassword,
        }),
      });

      const data = await response.json();

      if (response.ok) {
        setSuccess("Registration successful!");
        setError("");
        // window.location.href = '/login';
      } else {
        setError(data.error || JSON.stringify(data));
        setSuccess("");
      }
    } catch (err) {
      setError("Something went wrong. Please try again.");
      setSuccess("");
    }
  };

  return (
    <div className="register-container">
      <div className="register-card">
        <h2>ComeIn Register</h2>

        {error && <p className="error-message">{error}</p>}
        {success && <p className="success-message">{success}</p>}

        <form className="register-form" onSubmit={handleSubmit}>
          <input
            type="text"
            className="register-input"
            placeholder="Full name"
            value={fullname}
            onChange={(e) => setFullname(e.target.value)}
            required
          />
          <input
            type="email"
            className="register-input"
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
          <input
            type="tel"
            className="register-input"
            placeholder="Phone number"
            value={phone}
            onChange={(e) => setPhone(e.target.value)}
            required
          />

          <div className="password-field">
            <input
              type={showPassword ? "text" : "password"}
              className="register-input"
              placeholder="Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
            <span
              className="toggle-icon"
              onClick={() => setShowPassword(!showPassword)}
            >
              {showPassword ? "🙈" : "👁️"}
            </span>
          </div>

          <div className="password-field">
            <input
              type={showConfirmPassword ? "text" : "password"}
              className="register-input"
              placeholder="Confirm Password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              required
            />
            <span
              className="toggle-icon"
              onClick={() => setShowConfirmPassword(!showConfirmPassword)}
            >
              {showConfirmPassword ? "🙈" : "👁️"}
            </span>
          </div>

          <button type="submit" className="register-btn">
            Register
          </button>
        </form>

        <button className="google-btn">
          <img
            src="https://www.svgrepo.com/show/355037/google.svg"
            alt="google"
          />{" "}
          Sign up with Google
        </button>

        <p className="login-link">
          Already have an account? <a href="/">Login</a>
        </p>
      </div>
    </div>
  );
}
