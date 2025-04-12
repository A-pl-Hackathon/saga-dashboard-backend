from pydantic import BaseModel, Field

class PersonalData(BaseModel):
    wallet_address: str = Field(
        ..., 
        alias="wallet-address",
        description="Ethereum wallet address"
    )
    data: str = Field(
        ...,
        description="Additional personal data"
    )

    class Config:
        schema_extra = {
            "example": {
                "wallet-address": "0x71C7656EC7ab88b098defB751B7401B5f6d8976F",
                "data": "user personal information"
            }
        }

class UserRequest(BaseModel):
    publicKey: str = Field(
        ..., 
        description="Public key for authentication"
    )
    secretKey: str = Field(
        ..., 
        description="Secret key for authentication"
    )
    apiKey: str = Field(
        ..., 
        description="API key for third-party services"
    )
    personal_data: PersonalData = Field(
        ..., 
        alias="personal-data",
        description="User's personal data including wallet address"
    )

    class Config:
        schema_extra = {
            "example": {
                "publicKey": "sample-public-key",
                "secretKey": "sample-secret-key",
                "apiKey": "sample-api-key",
                "personal-data": {
                    "wallet-address": "0x71C7656EC7ab88b098defB751B7401B5f6d8976F",
                    "data": "user personal information"
                }
            }
        }
