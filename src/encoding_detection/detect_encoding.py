from urllib.request import urlopen
from chardet import detect as guess_encoding
from os import path

ENCODINGS_FILE = path.join(path.dirname(path.abspath(__file__)),"encodings.txt")

def detect(raw_data):
    guess = guess_encoding(raw_data)
    encoding = guess["encoding"]
    if guess["confidence"] > 0.8:
        return encoding
    try:
        raw_data.decode(encoding)
        return encoding
    except:
        encoding = None
    for encoding in _all_encodings():
        try:
            raw_data.decode(encoding)
            return encoding
        except:
            pass
    return "utf-8"

def _all_encodings():
    encodings = []
    try:
        with open(ENCODINGS_FILE) as codecs:
            for codec in codecs:
                encodings.append(codec.replace("\n",""))
        return encodings
    except:
        _update_encodings()
        return _all_encodings()

def _update_encodings():
    python_version = 5.0
    response = None
    while python_version > 0:
        url = "https://docs.python.org/"+str(round(python_version,1))+"/library/codecs.html"
        try:
            response = urlopen(url,timeout=5).read().decode("utf-8")
            break
        except:
            python_version -= 0.1
    if response is None:
        return None
    response = response.split("<h2>Standard Encodings")[1].split("<h2>Python Specific Encodings")[0]
    encodings = []
    for line in response.split("\n"):
        if any(text_string in line for text_string in ("<tr class=","<tr class=")):
            line = line.split("<p>")[1].split("</p>")[0]
            encodings.append(line)
    text_file = open(ENCODINGS_FILE,"w")
    for encoding in encodings:
        text_file.write(encoding+"\n")
    text_file.close()
