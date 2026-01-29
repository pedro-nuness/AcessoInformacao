from presidio_analyzer import Pattern, PatternRecognizer

class PasswordRecognizer(PatternRecognizer):
    def __init__(self):
        patterns = [
            Pattern(
                name="password_pattern", 
                regex=r"(?i)\b(?:senha|password|passwd|pin|secret|token)\b\s*(?:[:=]|\sé\s|\sis\s)\s*(\S+)",
                score=0.7)
        ]
        
        super().__init__(
            supported_entity="SENHA",
            patterns=patterns,
            supported_language="pt"
        )