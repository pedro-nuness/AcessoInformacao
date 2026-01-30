from presidio_analyzer import AnalyzerEngine, RecognizerRegistry
from presidio_analyzer.nlp_engine import NlpEngineProvider
from presidio_anonymizer import AnonymizerEngine
from app.services.pii_detector.settings import SPACY_CONFIG
from app.services.pii_detector.custom_patterns import RECOGNIZERS

class PIIPresidioScanner:
    def __init__(self):

        provider = NlpEngineProvider(nlp_configuration=SPACY_CONFIG)
        nlp_engine = provider.create_engine()

        registry = RecognizerRegistry()
        registry.load_predefined_recognizers(languages=["pt"])
        
        for recognizer in RECOGNIZERS:
            registry.add_recognizer(recognizer)

        self.analyzer = AnalyzerEngine(registry=registry, nlp_engine=nlp_engine)
        self.anonymizer = AnonymizerEngine()

    def analyze_text(self, text):
        return self.analyzer.analyze(
            text=text, 
            language='pt',
            score_threshold=0.4
        )