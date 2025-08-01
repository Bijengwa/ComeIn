import './App.css';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Register from './components/auth/register';
import Login from './components/auth/login'; 
import VerificationPage from './components/auth/auth verify/VerificationPage';
import Dashboard from './components/dashboard/dashboard.js'
import ForgotPassword from './components/auth/forgotPassword/forgotPassword.js';
import ResetPassword from './components/auth/resetPassword/ResetPassword.js';

function App() {
  return (
    <Router>

      <Routes>
        <Route path="/" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/verify" element={<VerificationPage />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path='/forgot-password' element={<ForgotPassword />} />
        <Route path='/reset-password' element={<ResetPassword />} />
      </Routes>
    </Router>
  );
}

export default App;