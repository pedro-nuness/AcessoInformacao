import asyncio
from typing import Dict
from app.services.pii_detector.scanner import PIIScanner

GLOBAL_SCANNER = PIIScanner()

async def analyze_text(text: str) -> Dict:
    pii_results = await asyncio.to_thread(GLOBAL_SCANNER.analyze_text, text)

    anonymized_result = await asyncio.to_thread(
        GLOBAL_SCANNER.anonymize_text, 
        text, 
        pii_results
    )

    detections = [
        {
            "type": res.entity_type,
            "score": round(res.score, 2),
            "start": res.start,
            "end": res.end,
            "value": text[res.start:res.end] 
        }
        for res in pii_results
    ]

    return {
        "summary": text[:100] + "..." if len(text) > 100 else text,
        "length": len(text),
        "pii_count": len(pii_results),
        "pii_detected": detections,
        "anonymized_text": anonymized_result.text
    }

