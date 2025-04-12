import os
import requests
from fastapi import FastAPI, HTTPException
from schemas import UserRequest
from services.key_management import create_eth_keypair
from services.blockchain import get_token_balance
from dotenv import load_dotenv

load_dotenv()

EXISTING_SERVER_URL = os.getenv("EXISTING_SERVER_URL")

app = FastAPI(
    title="Token Balance & Key Management API",
    description="Generate Ethereum keys and process user data",
    version="1.0.0",
)

@app.post("/user-data/")
def process_user_data(request: UserRequest):

    wallet_address = request.personalData.walletAddress

    # 새 키 쌍 생성 (백엔드 전용)
    backend_private_key, backend_public_address = create_eth_keypair()

    # ERC-20 잔액 조회 (사용자 지갑)
    try:
        balance_token = get_token_balance(wallet_address)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Token balance retrieval failed: {str(e)}")

    # 기존 서버에 프라이빗 키 및 사용자 데이터 전송
    payload = {
        "personalData": {
            "walletAddress": wallet_address,
            "data": request.personalData.data
        },
        "agentModel": request.agentModel,
        "backendPrivateKey": backend_private_key  # 추가: 백엔드 전용 개인키
    }

    try:
        response = requests.post(
            f"{EXISTING_SERVER_URL}/external",
            json=payload
        )
        response.raise_for_status()
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Failed to send data to 8000 server: {str(e)}")

    # 사용자(프론트엔드)에는 백엔드 공개키 반환
    return {
        "userWalletAddress": wallet_address,
        "userTokenBalance": str(balance_token),
        "token": "MTK",
        "backendPublicAddress": backend_public_address,  # 프론트로 공개키 반환
        "message": "Data processed successfully, backend key generated."
    }

@app.get("/")
def read_root():
    return {"message": "Welcome to the Token Balance & Key Management API. See /docs for details."}
