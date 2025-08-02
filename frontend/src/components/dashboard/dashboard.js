import React, { useEffect, useState } from "react";
import { FaSearch, FaStore, FaCompass, FaUserCircle, FaQuestionCircle, FaBars } from "react-icons/fa";
import "./dashboard.css";

export default function Dashboard() {
    const [userName, setUserName] = useState("");
    const [quote, setQuote] = useState("");
    const [sidebarOpen, setSidebarOpen] = useState(true); // toggle sidebar

    const quotes = [
        "Start where you are. Use what you have. Do what you can.",
        "Every sale brings you closer to success.",
        "Let your product speak louder than ads.",
        "Serve someone today. Make a difference.",
        "Turn passion into profit."
    ];

    useEffect(() => {
        const storedName = localStorage.getItem("userFullName");
        if (storedName) {
            setUserName(storedName);
        }

        const interval = setInterval(() => {
            const randomIndex = Math.floor(Math.random() * quotes.length);
            setQuote(quotes[randomIndex]);
        }, 8000); // change every 8 seconds

        return () => clearInterval(interval);
    }, []);

    return (
        <div className={`dashboard-container ${sidebarOpen ? "open" : "collapsed"}`}>
            <div className="welcoming-top">
                <h1 id="welcome-note">ComeIn, {userName}</h1>
                <p id="inspiration-note">{quote}</p>
            </div>

            <div className="body-container">
                <div className="sidebar-container">
                    <div className="sidebar-toggle" onClick={() => setSidebarOpen(!sidebarOpen)}>
                        <FaBars />
                    </div>
                    <div className={`sidebar ${sidebarOpen ? "wide" : "thin"}`}>
                    <ul className="top-ul">
                        <li className="top-li">
                            <FaCompass className="icon" />
                            {sidebarOpen && <span>Explore</span>}
                        </li>
                        <li className="top-li">
                            <FaStore className="icon" />
                            {sidebarOpen && <span>inShop</span>}
                        </li>
                        <li className="top-li">
                            <FaSearch className="icon" />
                            {sidebarOpen && <span>Search</span>}
                        </li>
                    </ul>
                    <ul className="bottom-ul">
                        <li className="bottom-li" onClick={() => window.location.href = "/profile"}>
                            <FaUserCircle className="icon profile-icon" />
                            {sidebarOpen && <span>Profile</span>}
                        </li>
                        <li className="bottom-li">
                            <FaQuestionCircle className="icon" />
                            {sidebarOpen && <span>Help</span>}
                        </li>
                    </ul>
                    </div>
                </div>

                <div className="main-content">
                    {/* Add product/service grid here */}
                </div>
            </div>
        </div>
    );
}
