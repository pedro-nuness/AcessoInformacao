from typing import Dict


async def analyze_text(text: str) -> Dict:
    return {"summary": text[:200], "length": len(text)}
def analyze_text(text: str) -> dict:
    return {"confidence": 0.95, "data": {"summary": "This is a summary of the text."}}
