# Users Module Monorepo

Welcome to the **Users Module** monorepo. This repository contains both the backend services and the frontend management console dashboard.

## 📂 Repository Structure

- [**`BACKEND/`**](file:///Users/shakib/Downloads/Drive/Work/Github_Repos/Users-Module/BACKEND): A FastAPI-based backend application providing authentication, authorization, and RBAC user lifecycle controls.
- [**`FRONTEND/`**](file:///Users/shakib/Downloads/Drive/Work/Github_Repos/Users-Module/FRONTEND): A React + Vite dashboard interface for configuring roles, groups, permissions, and viewing active user logs.

---

## 🚀 Getting Started

### 1. Running the Backend
Navigate to the `BACKEND` directory:
```bash
cd BACKEND
```
Follow the instructions in [`BACKEND/README.md`](file:///Users/shakib/Downloads/Drive/Work/Github_Repos/Users-Module/BACKEND/README.md) to set up your virtual environment, run migrations, and spin up the development server:
```bash
uvicorn app.main:app --reload
```

### 2. Running the Frontend
Navigate to the `FRONTEND` directory:
```bash
cd FRONTEND
```
Install dependencies and start the Vite development server:
```bash
npm install
npm run dev
```

---

## ⚙️ CORS & Render Deployment
- The frontend is pre-configured to communicate with the Render API hosted at `https://users-module.onrender.com/`.
- Backend supports CORS from standard local environments (`localhost:5173`) and designated GitHub Pages domains.
- A **Cold Start Loader Overlay** has been implemented on the frontend to notify users when the backend is spinning up from inactivity on Render's free tier (which takes ~50 seconds).
