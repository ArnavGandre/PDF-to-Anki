import re
def extract_sentences(text):
    extracted_sentences = []
    sentences = re.split(r'\.\s+(?=[A-Z])', text)    
    for sentence in sentences:
        cleaned = sentence.replace('\r', ' ').replace('\n', ' ')
        cleaned = re.sub(r'\s+\d+$', '', cleaned)
        cleaned = cleaned.strip()
        if len(cleaned) > 3:
            extracted_sentences.append(cleaned)
    return extracted_sentences