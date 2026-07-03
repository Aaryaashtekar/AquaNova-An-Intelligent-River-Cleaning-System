
# AquoNova Dashboard Full Stack Project

## Features Added
- Google Authentication
- Admin Login System
- MongoDB Atlas Connectivity
- Backend API using Express.js
- Frontend + Backend Integration

---

# Steps to Execute Project

## 1. Install Node.js
Download and install Node.js.

---

## 2. Setup Backend

Open terminal inside backend folder.

Run:

npm install

After installation start backend:

npm run dev

---

## 3. Setup MongoDB Atlas

1. Create account on MongoDB Atlas
2. Create cluster
3. Click Connect
4. Select Drivers
5. Copy connection string

Paste inside backend/.env

Example:

MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/aquonova

---

## 4. Setup Google Authentication

1. Open Firebase Console
2. Create project
3. Enable Authentication
4. Enable Google Sign In
5. Copy Firebase Config

Paste config inside frontend/script.js

---

## 5. Run Frontend

Open frontend/index.html in browser.

OR use Live Server extension in VS Code.

---

## 6. Admin Login

Set admin email inside backend/.env

Example:

ADMIN_EMAIL=yourgmail@gmail.com

When this email logs in using Google, Admin Panel becomes visible.

