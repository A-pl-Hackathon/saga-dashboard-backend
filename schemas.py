from pydantic import BaseModel, Field

class PersonalData(BaseModel):
    walletAddress: str = Field(
        ..., 
        description="Ethereum wallet address"
    )
    data: str = Field(
        ..., 
        description="Additional personal data"
    )

    class Config:
        schema_extra = {
            "example": {
                "walletAddress": "0x71C7656EC7ab88b098defB751B7401B5f6d8976F",
                "data": "user personal information"
            }
        }

class UserRequest(BaseModel):
    personalData: PersonalData = Field(
        ..., 
        description="User's personal data including wallet address"
    )
    agentModel: str = Field(
        ...,
        description="Agent model identifier"
    )
    prompt: str = Field(
        default="",
        description="Optional prompt for the agent"
    )

    class Config:
        schema_extra = {
            "example": {
                "personalData": {
                    "walletAddress": "0x71C7656EC7ab88b098defB751B7401B5f6d8976F",
                    "data": "user personal information"
                },
                "agentModel": "sample-agent-model",
                "prompt": ""
            }
        }
