# Debt Collection Agency (DCA) Management System

A full-stack web application developed during the **FedEx SMART India Hackathon 2026** to streamline debt collection operations for **FedEx enterprise teams**. The platform enables secure management of customer debt cases, assignment of recovery tasks to collection agents, and tracking of collection progress through a centralized system.

---

## Features

### Admin
- Create and manage user accounts
- Manage collection agents
- Monitor customer debt cases
- Assign recovery tasks
- Track overall collection progress

### Collection Agent
- View assigned debt cases
- Update collection status
- Record recovery progress
- Maintain customer interaction records

---

## Tech Stack

### Frontend
- Vue.js
- HTML
- CSS
- Axios

### Backend
- Flask
- SQLAlchemy

### Database
- PostgreSQL

---

## Project Structure

```
FedEx-Smart-Hackathon-DCA-Management-System/
│
├── backend/
│   ├── app.py
│   ├── models.py
│   ├── routes/
│   ├── migrations/
│   └── requirements.txt
│
└── frontend/
    ├── src/
    ├── public/
    ├── package.json
    └── vite.config.js
```

---

## Setup

### Backend

```bash
cd backend

python -m venv venv

# Windows
venv\Scripts\activate

pip install -r requirements.txt

flask db upgrade

python app.py
```

Backend runs at:

```
http://127.0.0.1:5000
```

---

### Frontend

```bash
cd frontend

npm install

npm run dev
```

Frontend runs at:

```
http://localhost:5173
```

---

## Workflow

1. Administrator creates user accounts.
2. Customer debt cases are registered.
3. Recovery tasks are assigned to collection agents.
4. Agents update collection progress.
5. Administrators monitor debt recovery through a centralized dashboard.

---

## Highlights

- Secure authentication and role-based access control
- Full-stack architecture using Vue.js and Flask
- Relational database design using PostgreSQL and SQLAlchemy
- Modular backend structure for scalable development
- Developed collaboratively during the **FedEx SMART India Hackathon 2026**

---

## Team

Developed by a team of **3 members** during the **FedEx SMART India Hackathon 2026**.