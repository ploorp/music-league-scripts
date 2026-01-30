import re

def unique_words(text):
    text = re.sub(r"\[[^\]]*\]", "", text).lower().replace("’", "'")
    text = re.sub(r"[^\w'\-\s]", " ", text, flags=re.UNICODE)
    return set(text.split())

def main():
    lyrics = input("enter lyrics in genius format: ")
    words = unique_words(lyrics)
    print(f"unique wc: {len(words)}")