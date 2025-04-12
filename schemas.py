from pydantic import BaseModel, Field

class PersonalData(BaseModel):
    wallet_address: str = Field(..., alias="wallet-address")
    data: str

class UserRequest(BaseModel):
    publicKey: str
    secretKey: str
    apiKey: str
    personal_data: PersonalData = Field(..., alias="personal-data")
