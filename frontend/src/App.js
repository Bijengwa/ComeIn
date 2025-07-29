import './App.css';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import Register from './components/auth/register';
import Login from './components/auth/login'; // create this later

function App() {
  return (
    <Router>
      <nav style={{ marginBottom: '20px' }}>
        <Link to="/" style={{ marginRight: '10px' }}>Login</Link>
        <Link to="/register">Register</Link>
      </nav>

      <Routes>
        <Route path="/" element={<Login />} />
        <Route path="/register" element={<Register />} />
      </Routes>
    </Router>
  );
}

export default App;
