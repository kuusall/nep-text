import re
def clean_text(text):
    """Clean and normalize text content"""
    if not text:
        return ""
    
    # Remove unwanted characters but keep Nepali text
    text = re.sub(r'[^\u0900-\u097F\s\w\.,!?;:()\-\'\"]+', '', text)
    text = text.replace('\u2013', ' ')  # Replace en-dash
    text = text.replace('\u2014', ' ')  # Replace em-dash
    text = re.sub(r'\s+', ' ', text)    # Replace multiple spaces with single space
    text = re.sub(r'[a-zA-Z0-9/.-'']', '', text)
    
    return text.strip()