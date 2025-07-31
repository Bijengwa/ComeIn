import React from "react";

// Dashboard component displays the main area after login
export default function Dashboard() {
    return (
        <div className="dashboard-container">
            <h1>Welcome to the Dashboard</h1>

            <div className="dashboard-content">
                {/* Add your widgets, summaries, cards, or components here */}
                <p>This is your main dashboard. Customize this area as needed.</p>
            </div>
        </div>
    );
}
