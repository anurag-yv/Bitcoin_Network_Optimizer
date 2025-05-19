Bitcoin Network Optimizer Dashboard
A full-stack web application built for the Bitcoin 2025 Hackathon to visualize real-time Bitcoin network data, helping users optimize transaction timing and minimize fees. Developed from April 7 to May 20, 2025, this project provides an intuitive dashboard with mempool size, transaction fees, and network difficulty insights, powered by the mempool.space API and WebSocket updates.
Table of Contents

Features
Tech Stack
Installation
Usage
Project Structure
Challenges and Solutions
Third-Party Licenses
Contributing
License
Contact

Features

Real-Time Data Visualization: Displays mempool transaction count, hourly fees, and transaction volume using Chart.js, updated via WebSocket servers (ports 8765/8766).
User Authentication: Secure login, registration, and logout with bcrypt password hashing and Flask session management.
Responsive UI: Styled with Tailwind CSS for a clean, mobile-friendly experience.
Bitcoin Insights: Helps users time transactions to save fees by analyzing mempool.space API data (e.g., fee dips, network congestion).
Robust Backend: Flask handles API requests, WebSocket streams, and user sessions with logging for debugging.

Tech Stack

Backend: Flask, Python, bcrypt, WebSocket (websockets library), psutil, requests
Frontend: HTML, JavaScript, Chart.js, Tailwind CSS
APIs: mempool.space for fees, mempool, and difficulty adjustment data
Development Tools: VS Code, Git, Python 3.8+

Installation
Clone the repository and set up the environment:
git clone https://github.com/anurag-yv/Bitcoin_Network_Optimizer

Install dependencies:
pip install -r requirements.txt

Requirements:

Python 3.8 or higher
Dependencies listed in requirements.txt:
flask
flask-cors
requests
websockets
psutil
bcrypt



Usage

Run the Flask application:
python app.py


The server starts at http://localhost:5000.
WebSocket servers run on ws://localhost:8765 or ws://localhost:8766 (failover).


Open http://localhost:5000/user or live server in a browser (Chrome/Firefox, non-incognito).

Register: Create a user (e.g., username: testuser, password: password123).

Login: Log in to access the dashboard.

Dashboard: View real-time charts for mempool size, fees, and transaction volume. Use the data to optimize Bitcoin transactions (e.g., send during low-fee periods).

Logout: Securely log out to clear the session.


Note: Ensure ports 5000, 8765, and 8766 are free. The app automatically handles port conflicts by switching to 8766 if 8765 is in use.
Project Structure
bitcoin-network-optimizer/
├── static/                 # Static files (CSS, JS, images)
│   ├── app.js             # Frontend logic and Chart.js integration
│   
├── templates/              # HTML templates
│   ├── index.html         # Homepage
│   ├── user.html          # Login/register page
│   └── dashboard.html     # Dashboard with charts
├── app.py                 # Flask backend (API, WebSocket, auth)
├── requirements.txt       # Python dependencies
├── README.md              # This file
└── LICENSE                # MIT license

Challenges and Solutions
During the hackathon (April 7–May 20, 2025), I encountered and resolved:

Server Error (HTTP 500) in Login: A TypeError in app.py’s /login endpoint was fixed by adding JSON validation and detailed logging (logger.info("Request JSON: {data}")). Ensured Content-Type: application/json in user.html’s fetch request.
Dashboard 404: The /dashboard route failed due to a missing dashboard.html. Resolved by creating and placing dashboard.html in templates/, with error handling in app.py (try/except for TemplateNotFound).
Session Persistence: Dynamic app.secret_key caused session issues. Fixed by using a static key (your-static-secret-key-12345).
WebSocket Stability: Port conflicts on 8765 were addressed by implementing failover to 8766 using psutil and socket.

These solutions demonstrate robust problem-solving, aligning with the hackathon’s Routine Execution criterion.
Third-Party Licenses

mempool.space API: Used under their terms for non-commercial, open-source projects. Data fetched for fees, mempool, and difficulty adjustment.
bcrypt: Apache License 2.0, used for password hashing.
Chart.js: MIT License, used for charts.
Tailwind CSS: MIT License, used for styling.
Flask, flask-cors, requests, websockets, psutil: Various open-source licenses (BSD, MIT, Apache), listed in requirements.txt.

All third-party tools comply with the Bitcoin 2025 Hackathon’s terms for submissions.
Contributing
Contributions are welcome! To contribute:

Fork the repository.
Create a feature branch: git checkout -b feature/your-feature.
Commit changes: git commit -m "Add your feature".
Push to the branch: git push origin feature/your-feature.
Open a pull request.

Please follow the Code of Conduct and ensure tests pass (if added).
License
This project is licensed under the MIT License.
Contact

Author: Anurag Yadav
GitHub: anurag-yv
Email:anuragyadavmzp2006@gmail.com

Built with 💻 and ⚡ for the Bitcoin 2025 Hackathon. Let’s make Bitcoin transactions smarter!
