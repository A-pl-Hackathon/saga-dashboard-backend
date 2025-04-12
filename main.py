import os
import requests
import uuid
from fastapi import FastAPI, HTTPException, Request, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel
from schemas import UserRequest
from services.key_management import create_eth_keypair, get_random_key_pair, get_specific_key_pair
from services.blockchain import get_token_balance
from dotenv import load_dotenv

load_dotenv()

EXISTING_SERVER_URL = os.getenv("EXISTING_SERVER_URL")

app = FastAPI(
    title="Token Balance & Key Management API",
    description="Generate Ethereum keys and process user data",
    version="1.0.0",
)

delegation_requests = {}

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

class DelegationConfirmation(BaseModel):
    request_id: str
    confirmed: bool

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
        # Use pre-generated key pair from key_pair.json 
        backend_private_key, backend_public_address = get_random_key_pair()

        # ERC-20 balance check (user wallet)
        try:
            balance_token = get_token_balance(wallet_address)
        except Exception as e:
            print(f"Token balance error: {str(e)}")
            # Just set balance to 0 and continue if there's an error
            balance_token = 0

        request_id = str(uuid.uuid4())
        
        delegation_requests[request_id] = {
            "personalData": {
                "walletAddress": wallet_address,
                "data": request.personalData.data
            },
            "agentModel": request.agentModel,
            "prompt": request.prompt,
            "backendPrivateKey": backend_private_key,
            "backendPublicAddress": backend_public_address,
            "userTokenBalance": str(balance_token)
        }
        
        return {
            "requestId": request_id,
            "userWalletAddress": wallet_address,
            "userTokenBalance": str(balance_token),
            "token": "MTK",
            "backendPublicAddress": backend_public_address,
            "message": "Please confirm delegation before proceeding."
        }
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

@app.post("/confirm-delegation/")
async def confirm_delegation(confirmation: DelegationConfirmation):
    if confirmation.request_id not in delegation_requests:
        raise HTTPException(status_code=404, detail="Delegation request not found or expired")
    
    request_data = delegation_requests[confirmation.request_id]
    
    if confirmation.confirmed:
        try:
            payload = {
                "personalData": request_data["personalData"],
                "agentModel": request_data["agentModel"],
                "prompt": request_data["prompt"],
                "backendPrivateKey": request_data["backendPrivateKey"]
            }

            print(f"Sending payload to external API: {payload}")
            response = requests.post(
                f"{EXISTING_SERVER_URL}/external",
                json=payload
            )
            response.raise_for_status()
            print(f"Response from external API: {response.status_code}")
            
            return {
                "success": True,
                "userWalletAddress": request_data["personalData"]["walletAddress"],
                "userTokenBalance": request_data["userTokenBalance"],
                "token": "MTK",
                "backendPublicAddress": request_data["backendPublicAddress"],
                "message": "Delegation confirmed and data processed successfully."
            }
        except requests.RequestException as e:
            print(f"Failed to send data to server: {str(e)}")
            raise HTTPException(status_code=502, detail=f"Failed to communicate with external server: {str(e)}")
        finally:
            del delegation_requests[confirmation.request_id]
    else:
        del delegation_requests[confirmation.request_id]
        return {
            "success": False,
            "message": "Delegation declined by user."
        }

# Add a new endpoint to get a specific key pair by ID
@app.get("/key-pair/{pair_id}")
async def get_key_pair(pair_id: int):
    try:
        if pair_id < 1 or pair_id > 10:
            raise HTTPException(status_code=400, detail="Pair ID must be between 1 and 10")
            
        private_key, public_address = get_specific_key_pair(pair_id)
        
        if not private_key or not public_address:
            raise HTTPException(status_code=404, detail=f"Key pair {pair_id} not found")
            
        return {
            "keyPairId": pair_id,
            "publicAddress": public_address,
            # For security, we only return a hint of the private key
            "privateKeyHint": f"{private_key[:6]}...{private_key[-4:]}"
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

@app.get("/")
def read_root():
    return {"message": "Welcome to the Token Balance & Key Management API. See /docs for details."}
