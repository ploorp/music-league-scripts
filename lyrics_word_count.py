import re

def unique_words(text):
    text = re.sub(r"\[[^\]]*\]", "", text).lower().replace("’", "'")
    text = re.sub(r"[^\w'\-\s]", " ", text, flags=re.UNICODE)
    return set(text.split())

def main():
    lyrics = """



"""

    words = unique_words(lyrics)
    print(f"wc: {len(words)}")