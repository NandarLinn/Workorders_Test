from pydantic import BaseModel

class Ask(BaseModel):
    question: str

    class Config:
        orm_mode = True