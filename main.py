import os
import requests
from fastapi import FastAPI, HTTPException
from schemas import UserRequest
from services.blockchain import get_token_balance
from dotenv import load_dotenv

load_dotenv()

EXISTING_SERVER_URL = os.getenv("EXISTING_SERVER_URL")

app = FastAPI()

@app.post("/user-data/")
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
