from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from .scrapper import scrapped_products

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:3000", 
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["Authorization"],
)

AUTH_TOKEN = "test_static_token"


def authenticate_token(token: str = Header(...)):
    if token != AUTH_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid authentication token")

@app.get('/pages/{page}')
def home_pages(page: str | None = 1, authorization: str = Header(...)):
    authenticate_token(authorization)  # Check token before proceeding
    data = scrapped_products(page)
    return data


