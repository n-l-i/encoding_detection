from urllib.request import urlopen
from urllib.error import HTTPError
from chardet import detect as guess_encoding
from os import path

ENCODINGS_FILE = path.join(path.dirname(path.abspath(__file__)),"encodings.txt")

def detect(raw_data, confidence_treshhold=-1):
    guess = guess_encoding(raw_data)
    if guess["encoding"] is None:
        return _detect_correct_encoding(raw_data)
    if 0 <= confidence_treshhold <= guess["confidence"]:
        return guess["encoding"]
    try:
        raw_data.decode(guess["encoding"])
        return guess["encoding"]
    except (UnicodeDecodeError, LookupError):
        return _detect_correct_encoding(raw_data)

def _detect_correct_encoding(raw_data):
    encoding_candidates = []
    decoded_data = {}
    for encoding in _all_encodings():
        try:
            data = raw_data.decode(encoding)
            encoding_candidates.append(encoding)
            decoded_data[encoding] = data
        except UnicodeDecodeError:
            pass
    encoding_ranks = {}
    for encoding in encoding_candidates:
        n_same_answers = 0
        for other_encoding in encoding_candidates:
            if encoding == other_encoding:
                continue
            if decoded_data[encoding] == decoded_data[other_encoding]:
                n_same_answers += 1
        encoding_ranks[encoding] = n_same_answers
    highest_rank = max(encoding_ranks.values())
    for i in range(len(encoding_candidates)-1,-1,-1):
        if encoding_ranks[encoding_candidates[i]] != highest_rank:
            encoding_candidates.pop(i)
    return encoding_candidates[0]

def _all_encodings():
    encodings = []
    try:
        with open(ENCODINGS_FILE) as codecs:
            for codec in codecs:
                encodings.append(codec.replace("\n",""))
        return encodings
    except FileNotFoundError:
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
        except HTTPError:
            python_version -= 0.1
    if response is None:
        return None
    response = response.split("<h2>Standard Encodings")[1].split("<h2>Python Specific Encodings")[0]
    encodings = []
    for line in response.split("\n"):
        if any(text_string in line for text_string in ("<tr class=","<tr class=")):
            line = line.split("<p>")[1].split("</p>")[0]
            if line != "Codec":
                encodings.append(line)
    text_file = open(ENCODINGS_FILE,"w")
    for encoding in encodings:
        text_file.write(encoding+"\n")
    text_file.close()
