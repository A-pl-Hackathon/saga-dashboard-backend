import os
import requests
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
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

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://dashboard.a-pl.xyz",
        "http://dashboard.a-pl.xyz"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    body = exc.body
    if isinstance(body, bytes):
        try:
            body = body.decode('utf-8')
        except UnicodeDecodeError:
            body = str(body)
    
    errors = []
    for error in exc.errors():
        error_dict = dict(error)
        for key, value in error_dict.items():
            if isinstance(value, bytes):
                try:
                    error_dict[key] = value.decode('utf-8')
                except UnicodeDecodeError:
                    error_dict[key] = str(value)
        errors.append(error_dict)
    
    return JSONResponse(
        status_code=422,
        content={"detail": errors, "body": body},
    )

@app.post("/user-data/", response_model_exclude_unset=True)
async def process_user_data(request: UserRequest, raw_request: Request):
    try:
        raw_body = await raw_request.body()
        print(f"Raw request body: {raw_body}")
    except Exception as e:
        print(f"Failed to read raw request: {str(e)}")
    
    print(f"Received request: {request}")
    wallet_address = request.personalData.walletAddress

    try:
        # 새 키 쌍 생성 (백엔드 전용)
        backend_private_key, backend_public_address = create_eth_keypair()

        # ERC-20 잔액 조회 (사용자 지갑)
        try:
            balance_token = get_token_balance(wallet_address)
        except Exception as e:
            print(f"Token balance error: {str(e)}")
            # Just set balance to 0 and continue if there's an error
            balance_token = 0

        payload = {
            "personalData": {
                "walletAddress": wallet_address,
                "data": request.personalData.data
            },
            "agentModel": request.agentModel,
            "prompt": request.prompt,
            "backendPrivateKey": backend_private_key
        }

        try:
            print(f"Sending payload to external API: {payload}")
            response = requests.post(
                f"{EXISTING_SERVER_URL}/external",
                json=payload
            )
            response.raise_for_status()
            print(f"Response from external API: {response.status_code}")
        except requests.RequestException as e:
            print(f"Failed to send data to server: {str(e)}")
            # Continue even if the existing server is unreachable
        
        # 사용자(프론트엔드)에는 백엔드 공개키 반환
        return {
            "userWalletAddress": wallet_address,
            "userTokenBalance": str(balance_token),
            "token": "MTK",
            "backendPublicAddress": backend_public_address,
            "message": "Data processed successfully, backend key generated."
        }
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

@app.get("/")
def read_root():
    return {"message": "Welcome to the Token Balance & Key Management API. See /docs for details."}
