🚀 Bitcoin Network Optimizer Dashboard
Welcome to the Bitcoin Network Optimizer Dashboard, a full-stack web app built for the Bitcoin 2025 Hackathon 🎉! This project empowers Bitcoin users to optimize transaction timing and minimize fees by visualizing real-time network data, such as mempool size, fees, and difficulty adjustments, using the mempool.space API and WebSocket updates. Developed from April 7 to May 20, 2025, it’s a user-friendly tool for traders, miners, and enthusiasts in the Bitcoin ecosystem.

📑 Table of Contents

What It Does
Features
Tech Stack
Installation
Usage
Project Structure
Challenges & Solutions
Third-Party Licenses
Contributing
License
Contact


🌟 What It Does
Bitcoin transactions can be costly and slow during network congestion. The Bitcoin Network Optimizer Dashboard solves this by providing real-time insights into:

Mempool size: Understand network congestion.
Transaction fees: Identify low-fee windows for cost savings.
Difficulty adjustments: Monitor mining trends.

With a secure login system and responsive charts, it helps users make data-driven decisions to enhance Bitcoin’s usability. Check out the demo video (replace with your video URL after uploading)!

✨ Features
Click to Explore Features

📊 Real-Time Charts: Visualize mempool count, hourly fees, and transaction volume with Chart.js, updated every 60 seconds via WebSocket (ports 8765/8766).
🔐 Secure Authentication: Login, register, and logout with bcrypt password hashing and Flask sessions.
📱 Responsive Design: Tailwind CSS ensures a seamless experience on desktop and mobile.
⚡ Bitcoin Optimization: Analyze fee dips and mempool trends to time transactions effectively.
🛠️ Robust Backend: Flask handles API requests, WebSocket streams, and logging for reliability.


🛠️ Tech Stack



Category
Tools



Backend
Flask, Python, bcrypt, WebSocket, psutil, requests


Frontend
HTML, JavaScript, Chart.js, Tailwind CSS


APIs
mempool.space (fees, mempool, difficulty)


Dev Tools
VS Code, Git, Python 3.8+



🔧 Installation
Click for Setup Instructions

Clone the Repository:
git clone https://github.com/anurag-yv/Bitcoin_Network_Optimizer.git
cd bitcoin-network-optimizer


Install Dependencies:
pip install -r requirements.txt

Ensure Python 3.8+ is installed. Dependencies include:
flask==2.3.3
flask-cors==4.0.0
requests==2.31.0
websockets==12.0
psutil==5.9.5
bcrypt==4.0.1


Verify Files:
Ensure app.py, templates/ (index.html, user.html, dashboard.html), and static/ (app.js) are present.



🚀 Usage
Click to Run the App

Start the Server:
python app.py


Flask runs on http://localhost:5000.
WebSocket servers use ws://localhost:8765 or ws://localhost:8766.


Access the App:

Open http://localhost:5000/user in Chrome/Firefox (non-incognito).
Register: Create a user (e.g., testuser, password123).
Login: Access the dashboard with charts and “Welcome, testuser”.
Explore: View real-time mempool and fee data to optimize transactions.
Logout: Clear session securely.


Troubleshooting:

Ensure ports 5000, 8765, and 8766 are free.
Check Flask logs for errors (e.g., ERROR - Error in login endpoint).




📂 Project Structure
bitcoin-network-optimizer/
├── static/                 # CSS, JS, images
│   ├── app.js             # Chart.js and frontend logic
│   
├── templates/              # HTML templates
│   ├── index.html         # Homepage
│   ├── user.html          # Login/register
│   └── dashboard.html     # Dashboard with charts
├── app.py                 # Flask backend
├── requirements.txt       # Dependencies
├── README.md              # This file
├── LICENSE                # MIT License
└── .gitignore             # Ignores venv/, __pycache__/


🛡️ Challenges & Solutions
Click to View Challenges
Built during the Bitcoin 2025 Hackathon (April 7–May 20, 2025), I tackled:

🛑 Server Error (HTTP 500): Fixed a /login TypeError by validating JSON (request.get_json()) and adding detailed logging in app.py.
🚫 Dashboard 404: Resolved by placing dashboard.html in templates/ and handling TemplateNotFound errors.
🔑 Session Issues: Switched to a static app.secret_key for persistent sessions.
🌐 WebSocket Conflicts: Implemented port failover (8765 to 8766) using psutil and socket.

These solutions showcase robust debugging for the hackathon’s Routine Execution criterion.

📜 Third-Party Licenses

mempool.space API: Non-commercial use, per their terms.
bcrypt: Apache License 2.0.
Chart.js: MIT License.
Tailwind CSS: MIT License.
Flask, flask-cors, requests, websockets, psutil: BSD/MIT/Apache licenses.

All comply with Bitcoin 2025 Hackathon and Devpost terms.

🤝 Contributing
Love Bitcoin and want to help? Here’s how:

Fork the repo.
Create a branch: git checkout -b feature/your-feature.
Commit: git commit -m "Add your feature".
Push: git push origin feature/your-feature.
Open a pull request.

Follow the Code of Conduct (optional, add if desired).

📄 License
This project is licensed under the MIT License.

📬 Contact

Author: Anurag Yadav
GitHub: anurag-yv
Email: anuragyadavmzp2006@gmail.com

Built with 💻 and ⚡ for the Bitcoin 2025 Hackathon. Let’s optimize Bitcoin together! 🚀
