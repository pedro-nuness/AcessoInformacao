from presidio_analyzer import AnalyzerEngine, RecognizerRegistry
from presidio_analyzer.nlp_engine import NlpEngineProvider
from presidio_anonymizer import AnonymizerEngine
from settings import SPACY_CONFIG
from custom_patterns import *

class PIIScanner:

    def __init__(self):

        provider = NlpEngineProvider(nlp_configuration=SPACY_CONFIG)
        nlp_engine = provider.create_engine()

        registry = RecognizerRegistry()
        registry.load_predefined_recognizers()

        recognizers = [CpfRecognizer(), CnpjRecognizer(), PasswordRecognizer(), CarPlateRecognizer()]
        
        for recognizer in recognizers:
            registry.add_recognizer(recognizer)


        self.analyzer = AnalyzerEngine(registry=registry, nlp_engine=nlp_engine)
        self.anonymizer = AnonymizerEngine()

    def analyze_text(self, text):
        """Retorna a lista de entidades encontradas"""
        return self.analyzer.analyze(text=text, language='pt')

    def anonymize_text(self, text, results):
        """Retorna o texto anonimizado"""
        return self.anonymizer.anonymize(text=text, analyzer_results=results)