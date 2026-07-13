from fastapi import FastAPI
from dotenv import load_dotenv
import os
from groq import Groq
from database import engine
from database import Base
from database import SessionLocal
from models import User
from fastapi.middleware.cors import CORSMiddleware

from schemas import UserRegister, UserLogin, Token,RecommendationRequest

from auth import (
    hash_password,
    verify_password,
    create_access_token,
    verify_token,
    security,
)
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials

load_dotenv()

client = Groq(
    api_key = os.getenv("GROQ_API_KEY")
)

print("API KEY =",os.getenv("GROQ_API_KEY"))
app = FastAPI(
    title="Buywise AI API",
    description="AI-powered product reccomendation API",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/ai-test")
def ai_test():
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "user",
                "content": "Hello from Buywise AI"
            }
        ]
    )

    return {
        "response": response.choices[0].message.content
    }

Base.metadata.create_all(bind=engine)
@app.get("/")
async def root():
    return {"message": "Welcome to Buywise AI API"}

@app.post("/register")
def register(user: UserRegister):
    db = SessionLocal()

    hashed_password = hash_password(user.password)
    new_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password
    )

    db.add(new_user)
    try:
        db.commit()
    except Exception as e:
        print(e)
        raise

    db.refresh(new_user)

    return {
        "message": "User registered successfully"
    }




@app.post("/login", response_model=Token)
def login(user: UserLogin):
    db = SessionLocal()

    db_user = db.query(User).filter(User.email == user.email).first()

    if not db_user:
        return {"message": "Invalid email or password"}

    if not verify_password(user.password, db_user.hashed_password):
        return {"message": "Invalid email or password"}

    access_token = create_access_token(
        data={"sub": db_user.email}
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

@app.post("/recommend")
def recommend(data: RecommendationRequest):

    prompt = f"""
    Recommend the best {data.category}
    under ₹{data.budget}.

    Purpose: {data.purpose}

    Priority: {data.priority}

    Give:
    1. Top 3 recommendations
    2. Pros
    3. Cons
    4. Final recommendation
    """

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return {
        "recommendation": response.choices[0].message.content
    }

@app.get("/profile")
def profile(credentials: HTTPAuthorizationCredentials = Depends(security)):
    payload = verify_token(credentials.credentials)

    return {
        "message": "Welcome",
        "user": payload
    }

@app.get("/check-key")
def check_key():
    return {
        "api_key": os.getenv("GEMINI_API_KEY")
    }

@app.get("/models")
def models():
    return[m.name for m in client.models.list()]