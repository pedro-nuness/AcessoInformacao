from typing import Dict


async def analyze_text(text: str) -> Dict:
    # Async implementation for compatibility with worker await
    # Return structure matches Result model: confidence and data
    return {"confidence": 0.95, "data": {"summary": text[:200] if text else "", "length": len(text) if text else 0}}
