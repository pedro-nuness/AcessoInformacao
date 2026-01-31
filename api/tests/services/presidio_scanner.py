import pytest
from app.services.pii_detector.presidio_scanner import PresidioScanner

@pytest.fixture(scope="module")
def scanner():
    return PresidioScanner()

@pytest.mark.parametrize("text, expected_pii", [
    # PRIVATE
    ("Meu telefone é (61) 99876-5432", True),
    ("Ligar para 3344-5566 falar com Maria", True),
    ("Contato via whatsapp: 988776655", True),
    ("Meu CPF é 000.000.000-00", True),
    ("E-mail: danielle@unb.br", True),
    # PUBLIC
    ("Matrícula nº 78965412", False),
    ("Inscrição imobiliária 65478921 no 8º RI", False),
    ("Protocolo de atendimento: 20240101-99", False),
    ("O edital 01/2026 foi publicado ontem", False),
    ("Mandei um e-mail mas ele não respondeu", False),
])
def test_presidio_detection(scanner, text, expected_pii):
    results = scanner.analyze_text(text)
    
    has_pii = len(results) > 0
    
    assert has_pii == expected_pii, f"Falha no texto: '{text}'. Esperava PII={expected_pii}, mas obteve {has_pii}"

def test_check_phone_score(scanner):
    results = scanner.analyze_text("Matrícula 78965412")
    assert len(results) == 0