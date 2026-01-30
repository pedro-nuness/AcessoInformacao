from app.services.pii_detector.llm_scanner import LLMScanner
from app.services.pii_detector.presidio_scanner import PresidioScanner

GLOBAL_LLM_SCANNER = LLMScanner()
GLOBAL_PRESIDIO_SCANNER = PresidioScanner()

async def analyze_text(text: str) -> dict:
    presidio_results = GLOBAL_PRESIDIO_SCANNER.analyze_text(text)

    if len(presidio_results) > 0:
        entidades = sorted(list(set(res.entity_type for res in presidio_results)))
        
        return {
            "result": "PRIVATE",
            "details": f"Identificado pelo Presidio: {', '.join(entidades)}"
        }
    
    # segunda verificação com o Gemma, isso caso o presidio não encontre nada
    raw_gemma_response = await GLOBAL_LLM_SCANNER.analyze_text(text)
    
    should_be_private = raw_gemma_response.upper().startswith('Y')
    reason = raw_gemma_response[2:].strip() if len(raw_gemma_response) > 1 else "Não especificado"

    return {
        "result": "PRIVATE" if should_be_private else "PUBLIC",
        "details": reason if should_be_private else "Texto analisado e classificado como seguro."
    }