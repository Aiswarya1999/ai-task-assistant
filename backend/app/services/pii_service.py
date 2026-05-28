from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine

class PIIScrubber:
    def __init__(self):
        self.analyzer = AnalyzerEngine()
        self.anonymizer = AnonymizerEngine()

    def clean_text(self, text: str):
        results = self.analyzer.analyze(text=text, language='en')

        anonymized_result = self.anonymizer.anonymize(
            text=text,
            analyzer_results=results
        )
        return anonymized_result.text
scrubber = PIIScrubber()