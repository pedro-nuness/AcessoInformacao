from presidio_analyzer import Pattern, PatternRecognizer

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