from typing import Any
from fastapi import APIRouter
from schemas.ask import Ask
from modules.prompt_to_query import convert_prompt_to_query


router = APIRouter()

@router.post("/ask")
def ask_bot(
    input: Ask,
) -> Any:
    result = convert_prompt_to_query(input.question)
    return {"message": f"User asked: {result}"}
