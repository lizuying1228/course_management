# Course Management Frontend

React + TypeScript + Vite + Ant Design frontend for the Django REST Framework course management system.

## Requirements

- Node.js 20.19+ or 22.12+
- npm
- Django backend running at `http://127.0.0.1:8000`

## Install and run

From this directory:

```bash
npm install
npm run dev
```

Open `http://localhost:5173`.

The Vite development server proxies `/api/*` requests to Django at `http://127.0.0.1:8000`. Keep the backend running in a separate terminal. If the backend uses another address, update `server.proxy` in `vite.config.ts`.

## Production build

```bash
npm run build
npm run preview
```

The generated static files are written to `dist/`.

## Features

- Token login, logout, current-user profile, student and teacher registration
- Role-aware navigation for administrators, teachers and students
- Course browsing, filtering, creation, editing and deletion according to backend permissions
- Student and teacher profile listing and permitted profile maintenance
- Enrollment listing, student enrollment and withdrawal
- Paginated tables, request error messages and responsive layout

The backend remains the authority for authorization. Hiding a control in the frontend does not replace server-side permission checks.
