from presidio_analyzer import Pattern, PatternRecognizer
import re

class CnpjRecognizer(PatternRecognizer):
    def __init__(self):
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
        return self.isCnpjValid(pattern_text)
    
    def isCnpjValid(self, cnpj):
        """ If cnpf in the Brazilian format is valid, it returns True, otherwise, it returns False. """

        if not isinstance(cnpj,str):
            return False
        
        cpf = re.sub("[^0-9]",'',cnpj)

        if len(cpf) != 14:
            return False

        sum = 0
        weight = [5,4,3,2,9,8,7,6,5,4,3,2]

        """ Calculating the first cpf check digit. """
        for n in range(12):
            value =  int(cpf[n]) * weight[n]
            sum = sum + value


        verifyingDigit = sum % 11

        if verifyingDigit < 2 :
            firstVerifyingDigit = 0
        else:
            firstVerifyingDigit = 11 - verifyingDigit

        """ Calculating the second check digit of cpf. """
        sum = 0
        weight = [6,5,4,3,2,9,8,7,6,5,4,3,2]
        for n in range(13):
            sum = sum + int(cpf[n]) * weight[n]

        verifyingDigit = sum % 11

        if verifyingDigit < 2 :
            secondVerifyingDigit = 0
        else:
            secondVerifyingDigit = 11 - verifyingDigit

        if cpf[-2:] == "%s%s" % (firstVerifyingDigit,secondVerifyingDigit):
            return True
        return False
