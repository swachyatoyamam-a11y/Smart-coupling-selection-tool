# Smart Coupling Selection & Recommendation Tool

A full-stack engineering decision-support application based on the supplied project report. It uses a transparent rule-based FastAPI recommendation engine and a responsive React/Tailwind interface.

## Run locally

Open two terminals:

```powershell
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

```powershell
cd frontend
npm install
npm run dev
```

Visit `http://localhost:5173`.

## Deployment

- Frontend: deploy `frontend/` on Vercel. Set `VITE_API_URL` to the deployed API URL.
- Backend: deploy `backend/` on Render with start command `uvicorn main:app --host 0.0.0.0 --port $PORT`.
