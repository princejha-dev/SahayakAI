from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import query, escalations, audit

app = FastAPI(title="SahayakAI Backend", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "https://*.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(query.router)
app.include_router(escalations.router)
app.include_router(audit.router)

@app.get("/")
def root():
    return {"status": "SahayakAI backend running"}
