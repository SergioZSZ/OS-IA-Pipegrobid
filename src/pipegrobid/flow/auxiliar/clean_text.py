import re
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

import nltk



def clean_text(text: str) -> str:
    STOPWORDS = stopwords.words("english")
    lem = WordNetLemmatizer()

    text = text.lower() #minus
    text = re.sub(r"<.*?>", " ", text)  #etiquetas xml
    text = re.sub(r"http\S+|www\.\S+", " ", text)   #urls
    text = re.sub(r"\d+", " ", text)    #digitos
    text = re.sub(r"[^\w\s]", " ", text)    #cualquier cosa que no sea letra o espacios
    text = re.sub(r"\s+", " ", text).strip()    #mas de un espacio y espacio final/inicial

    #tokenizacion
    tokens = []
    for tok in text.split():
        if tok in STOPWORDS:
            continue
        tok = lem.lemmatize(tok)
        tokens.append(tok)

    return " ".join(tokens)
