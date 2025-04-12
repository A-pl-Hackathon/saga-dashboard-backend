import os
import requests
from fastapi import FastAPI, HTTPException
from schemas import UserRequest
from services.blockchain import get_token_balance
from dotenv import load_dotenv

load_dotenv()

EXISTING_SERVER_URL = os.getenv("EXISTING_SERVER_URL")

app = FastAPI(
    title="Token Balance API",
    description="API to process user data and retrieve token balances",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

@app.post("/user-data/", summary="Process user data and get token balance", 
         description="Processes user wallet data, retrieves token balance, and forwards data to external service")
def process_user_data(request: UserRequest):
    wallet_address = request.personal_data.wallet_address

    # ERC-20 잔액 조회
    try:
        balance_token = get_token_balance(wallet_address)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    # 기존 서버에 데이터 전송
    payload = {
        "apiKey": request.apiKey,
        "personal-data": {
            "wallet-address": wallet_address,
            "data": request.personal_data.data
        }
    }

    try:
        response = requests.post(
            f"{EXISTING_SERVER_URL}/external",
            json=payload
        )
        response.raise_for_status()
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Failed to send data: {e}")

    return {
        "wallet_address": wallet_address,
        "token_balance": str(balance_token),
        "token": "MTK",
        "message": "Data processed and forwarded successfully."
    }

@app.get("/", summary="Root endpoint", description="Returns a welcome message")
def read_root():
    return {"message": "Welcome to the Token Balance API. Access /docs for Swagger documentation."}
