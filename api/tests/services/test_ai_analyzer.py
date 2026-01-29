import pytest
from app.services.ai_analyzer import analyze_text

@pytest.mark.asyncio
async def test_analise_assincrona_completa():
    texto_teste = "email danidani@gmaill.com e senha 0553193@!, mas a senha: 3213"


    result = await analyze_text(texto_teste)

    assert "summary" in result
    assert "pii_detected" in result
    assert "anonymized_text" in result

    assert result["pii_count"] > 0 # pra ver se ele detectou 
    
    final_text = result["anonymized_text"]

    print(result["anonymized_text"])

    assert "danidani@gmaill.com" not in final_text
    assert "066.319.351-64" not in final_text
    assert "*****" in final_text or "<EMAIL>" in final_text