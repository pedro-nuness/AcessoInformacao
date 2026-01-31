from presidio_analyzer import Pattern, PatternRecognizer
from validate_docbr import CNPJ, CPF, CNS, CNH, PIS, RENAVAM, TituloEleitoral


class RgRecognizer(PatternRecognizer):
    def __init__(self):
        patterns = [
            Pattern(
                name="rg_pattern",
                regex=r"\b\d{1,2}[\s.]?\d{3}[\s.]?\d{3}[\s-]?[\dX|dx]\b",
                score=0.4
            )
        ]
        
        super().__init__(
            supported_entity="RG",
            patterns=patterns,
            context=["rg", "registro", "geral", "identidade", "ssp", "emissor", "documento"],
            supported_language="pt"
        )

class BrPhoneRecognizer(PatternRecognizer):
    def __init__(self):
        patterns = [
            Pattern(
                name="br_phone_pattern",
                regex=r"\b(?:\(?\d{2}\)?\s?)?(?:9\s?)?\d{4}[\s-]?\d{4}\b",
                score=0.35
            )
        ]
        
        super().__init__(
            supported_entity="PHONE_NUMBER",
            patterns=patterns,
            context=["celular", "fone", "telefone", "zap", "whatsapp", "contato", "ligar", "tel"],
            supported_language="pt"
        )

class CnpjRecognizer(PatternRecognizer):
    def __init__(self):
        self.cnpj_validator = CNPJ()
        patterns = [
            Pattern(
                name="cnpj_pattern",
                regex=r"\b\d{2}[\s.]?\d{3}[\s.]?\d{3}[\s/]?\d{4}[\s-]?\d{2}\b",
                score=0.85
            )
        ]
        
        super().__init__(
            supported_entity="CNPJ",
            patterns=patterns,
            context=["cnpj", "documento", "cadastro"],
            supported_language="pt"
        )

    def validate_result(self, pattern_text: str) -> bool:
        return self.cnpj_validator.validate(pattern_text)

class CpfRecognizer(PatternRecognizer):
    def __init__(self):
        self.cpf_validator = CPF()

        patterns = [
            Pattern(
                name="cpf_pattern",
                regex=r"\b\d{3}[\s.-]?\d{3}[\s.-]?\d{3}[\s.-]?\d{2}\b",
                score=0.85
            )
        ]
        
        super().__init__(
            supported_entity="CPF",
            patterns=patterns,
            context=["cpf", "documento", "cadastro"],
            supported_language="pt"
        )

    def validate_result(self, pattern_text: str) -> bool:
        result = self.cpf_validator.validate(pattern_text)
        print(f'pattern_text + {result}')
        return self.cpf_validator.validate(pattern_text)

class CnsRecognizer(PatternRecognizer):
    def __init__(self):
        self.validator = CNS()

        patterns = [
            Pattern(
                name="cns_pattern",
                regex=r"\b\d{3}[\s.]?\d{4}[\s.]?\d{4}[\s.]?\d{4}\b",
                score=0.6
            )
        ]

        super().__init__(
            supported_entity="CNS",
            patterns=patterns,
            context=["sus", "saúde", "cartão", "médico", "paciente", "cns"],
            supported_language="pt"
        )

    def validate_result(self, pattern_text: str) -> bool:
        return self.validator.validate(pattern_text)

class CnhRecognizer(PatternRecognizer):
    def __init__(self):
        self.validator = CNH()

        patterns = [
            Pattern(
                name="cnh_pattern",
                regex=r"\b\d{11}\b",
                score=0.4
            )
        ]

        super().__init__(
            supported_entity="CNH",
            patterns=patterns,
            context=["cnh", "habilitação", "motorista", "condutor", "detran", "carteira"],
            supported_language="pt"
        )

    def validate_result(self, pattern_text: str) -> bool:
        return self.validator.validate(pattern_text)

class CarPlateRecognizer(PatternRecognizer):
    def __init__(self):
        patterns = [
            Pattern(
                name="plate_pattern",
                regex=r"\b[A-Z]{3}-?\d[\dA-J]\d{2}\b",
                score=0.85
            )
        ]
        
        super().__init__(
            supported_entity="CAR_PLATE",
            patterns=patterns,
            context=["placa", "veículo", "carro", "moto", "detran", "multa"],
            supported_language="pt"
        )

class PisRecognizer(PatternRecognizer):
    def __init__(self):
        self.validator = PIS()

        patterns = [
            Pattern(
                name="pis_pattern",
                regex=r"\b\d{3}[\s.]?\d{5}[\s.]?\d{2}[\s.-]?\d\b",
                score=0.6
            )
        ]

        super().__init__(
            supported_entity="PIS",
            patterns=patterns,
            context=["pis", "pasep", "nis", "nit", "trabalho", "previdência", "social"],
            supported_language="pt"
        )

    def validate_result(self, pattern_text: str) -> bool:
        return self.validator.validate(pattern_text)

class RenavamRecognizer(PatternRecognizer):
    def __init__(self):
        self.validator = RENAVAM()

        patterns = [
            Pattern(
                name="renavam_pattern",
                regex=r"\b\d{9,11}\b",
                score=0.4
            )
        ]

        super().__init__(
            supported_entity="RENAVAM",
            patterns=patterns,
            context=["renavam", "veículo", "carro", "moto", "detran", "ipva", "licenciamento"],
            supported_language="pt"
        )

    def validate_result(self, pattern_text: str) -> bool:
        return self.validator.validate(pattern_text)

class TituloEleitoralRecognizer(PatternRecognizer):
    def __init__(self):
        self.validator = TituloEleitoral()

        patterns = [
            Pattern(
                name="titulo_eleitor_pattern",
                regex=r"\b\d{4}[\s.]?\d{4}[\s.]?\d{4}\b",
                score=0.6
            )
        ]

        super().__init__(
            supported_entity="TITULO_ELEITORAL",
            patterns=patterns,
            context=["título", "eleitor", "votação", "zona", "seção", "eleitoral"],
            supported_language="pt"
        )

    def validate_result(self, pattern_text: str) -> bool:
        return self.validator.validate(pattern_text)

# por enquanto n consegui fazer funcionar muito bem :(
# TO-DO: refazer PasswordRecognizer
class PasswordRecognizer(PatternRecognizer):
    def __init__(self):
        patterns = [
            Pattern(
                name="password_pattern", 
                regex=r"(?i)\b(?:senha|password|passwd|pin|secret|token)\b\s*(?:[:=]|\b(?:é|is)\b)?\s*([^\s.,]+)",
                score=1)
        ]
        
        super().__init__(
            supported_entity="SENHA",
            patterns=patterns,
            supported_language="pt"
        )

class CustomEmailRecognizer(PatternRecognizer):
    def __init__(self):
        patterns = [
            Pattern(
                name="email_pattern",
                regex=r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
                score=1
            ),
        ]
        
        super().__init__(
            supported_entity="EMAIL",
            patterns=patterns,
            supported_language="pt",
            name="CustomEmailRecognizer"
        )


RECOGNIZERS = [
    BrPhoneRecognizer(),
    # RgRecognizer(),
    CpfRecognizer(),
    CustomEmailRecognizer()
]
