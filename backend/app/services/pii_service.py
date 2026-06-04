import re

class PIIScrubber:
    def __init__(self):
        self.phone_pattern = re.compile(r'\+?\d{1,4}?[-.\s]?\(?\d{1,3}?\)?[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9}')
        self.email_pattern = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
        self.name_marker_pattern = re.compile(r'(?:met with|call|attention to|attn:)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)', re.IGNORECASE)

    def clean_text(self, text: str) -> str:
        if not text:
            return ""
        
        # 1. Scrub Emails
        text = self.email_pattern.sub("<EMAIL>", text)
        
        # 2. Scrub Phone Numbers
        matches = self.phone_pattern.finditer(text)
        for match in sorted(matches, key=lambda x: x.start(), reverse=True):
            val = match.group()
            if len(re.sub(r'\D', '', val)) >= 10:
                text = text[:match.start()] + "<PHONE_NUMBER>" + text[match.end():]
                
        # 3. Scrub Names following markers
        name_matches = list(self.name_marker_pattern.finditer(text))
        for match in sorted(name_matches, key=lambda x: x.start(1), reverse=True):
            text = text[:match.start(1)] + "<PERSON>" + text[match.end(1):]
            
        return text

scrubber = PIIScrubber()