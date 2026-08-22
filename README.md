# 🌍 Globe Trotter — Odoo Hackathon Project

> A modern, full-stack travel planning and itinerary management platform built for seamless group and solo journeys.

---

## 🚀 Key Features

* **Authentication & Security:** Secure user registration, login, and session management using Flask-Login and Werkzeug password hashing.
* **Multi-City Itinerary Timeline:** Plan trips across multiple destinations with custom arrival/departure dates.
* **Interactive Leaflet Maps:** Automatically geocodes cities using OpenStreetMap (clamped to India) and drops interactive map markers.
* **Live Weather Integration:** Pulls real-time temperature and weather conditions for each stop using the Open-Meteo API.
* **Smart Budget & Expense Calculator:** Categorizes expenses with dynamic Chart.js pie charts and calculates **per-person split costs** for group travel.
* **Public Sharing Links:** Generate clean, read-only public links to share your travel schedule with friends and family instantly without requiring a login.
* **AI Travel Assistant:** Provides curated local sightseeing, food hotspots, and cultural highlights for each city stop.
* **Packing Checklist & Travel Notes:** Interactive packing list with status toggles and a secure bookings/notes locker.
* **Emergency & Safety Directory:** Quick-reference emergency helplines (National Emergency, Railway, Tourist, Police) built right into the trip view.
* **Export / Print View:** Generates an offline-friendly summary sheet optimized for printing or saving as a PDF.
* **Persistent Dark Mode:** Built-in Light/Dark theme toggle using Bootstrap 5.3 and local storage.

---

## 🛠️ Tech Stack

* **Backend:** Python, Flask, Flask-SQLAlchemy, Flask-Login
* **Frontend:** HTML5, Bootstrap 5.3, Jinja2 Templates, JavaScript (Chart.js & Leaflet.js)
* **Database:** SQLite

---

## ⚙️ Installation & Running Locally

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/thakkarharsh1572007-sudo/Globe-Trotter-for-odoo-hackathon-.git](https://github.com/thakkarharsh1572007-sudo/Globe-Trotter-for-odoo-hackathon-.git)
   cd Globe-Trotter-for-odoo-hackathon-