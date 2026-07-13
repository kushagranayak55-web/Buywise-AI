from pydantic import BaseModel,EmailStr

class UserRegister(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
        email: EmailStr
        password: str

class Token(BaseModel):
        access_token: str
        token_type: str

class RecommendationRequest(BaseModel):
    category: str
    budget: int
    purpose: str
    priority: str

