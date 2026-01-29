from presidio_analyzer import Pattern, PatternRecognizer
import re

class CpfRecognizer(PatternRecognizer):
    def __init__(self):
        patterns = [
            Pattern(
                name="cpf_pattern",
                regex=r"\b\d{3}\.\d{3}\.\d{3}-\d{2}\b",
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
        return self.isCpfValid(pattern_text)
    
    def isCpfValid(self, cpf):
        """ If cpf in the Brazilian format is valid, it returns True, otherwise, it returns False. """

        if not isinstance(cpf,str):
            return False
        
        cpf = re.sub("[^0-9]",'',cpf)
        
        if cpf=='00000000000' or cpf=='11111111111' or cpf=='22222222222' or cpf=='33333333333' or cpf=='44444444444' or cpf=='55555555555' or cpf=='66666666666' or cpf=='77777777777' or cpf=='88888888888' or cpf=='99999999999':
            return False

        if len(cpf) != 11:
            return False

        sum = 0
        weight = 10

        """ Calculating the first cpf check digit. """
        for n in range(9):
            sum = sum + int(cpf[n]) * weight

            weight = weight - 1

        verifyingDigit = 11 -  sum % 11

        if verifyingDigit > 9 :
            firstVerifyingDigit = 0
        else:
            firstVerifyingDigit = verifyingDigit

        """ Calculating the second check digit of cpf. """
        sum = 0
        weight = 11
        for n in range(10):
            sum = sum + int(cpf[n]) * weight

            weight = weight - 1

        verifyingDigit = 11 -  sum % 11

        if verifyingDigit > 9 :
            secondVerifyingDigit = 0
        else:
            secondVerifyingDigit = verifyingDigit

        if cpf[-2:] == "%s%s" % (firstVerifyingDigit,secondVerifyingDigit):
            return True
        return False