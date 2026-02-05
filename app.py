import os
import logging
import warnings

# 1. SILENCE VS CODE ERRORS (403 Forbidden noise)
os.environ["HF_HUB_OFFLINE"] = "1" # Set to "0" if you need to download the model first
os.environ["TRANSFORMERS_NO_ADVISORY_WARNINGS"] = "1"
logging.getLogger("transformers").setLevel(logging.ERROR)
logging.getLogger("huggingface_hub").setLevel(logging.ERROR)
warnings.filterwarnings("ignore")

from flask import Flask, render_template, request
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from spellchecker import SpellChecker

app = Flask(__name__)

# Initialize SpellChecker
spell = SpellChecker()

# Load AI Model (This takes ~1GB RAM)
MODEL_NAME = "prithivida/grammar_error_correcter_v1"
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME)

def fix_spelling(text):
    """Pass 1: Identifies and fixes typos like 'dacng' or 'incoroporate'"""
    words = text.split()
    corrected_words = []
    
    for word in words:
        # Strip punctuation for better checking
        clean_word = word.strip(".,!?").lower()
        misspelled = spell.unknown([clean_word])
        
        if misspelled:
            candidate = spell.correction(clean_word)
            if candidate:
                # Re-attach punctuation and maintain case
                if word[0].isupper():
                    corrected_words.append(candidate.capitalize())
                else:
                    corrected_words.append(candidate)
            else:
                corrected_words.append(word)
        else:
            corrected_words.append(word)
    
    return " ".join(corrected_words)

def get_correction(text):
    """Pass 2: Fixes grammar using the T5 Transformer model"""
    # Fix spelling first
    clean_text = fix_spelling(text)
    
    # AI Processing
    input_text = "gec: " + clean_text
    inputs = tokenizer.encode(input_text, return_tensors="pt", max_length=128, truncation=True)
    
    outputs = model.generate(
        inputs, 
        max_length=128, 
        num_beams=5,
        repetition_penalty=1.5, # Stops "her is is" errors
        no_repeat_ngram_size=2,
        early_stopping=True
    )
    
    corrected = tokenizer.decode(outputs[0], skip_special_tokens=True)
    
    # Final Polish: Capitalize and add a period if missing
    if corrected:
        corrected = corrected[0].upper() + corrected[1:]
        if not corrected.endswith(('.', '!', '?')):
            corrected += "."
            
    return corrected

@app.route('/', methods=['GET', 'POST'])
def index():
    original = ""
    corrected = ""
    if request.method == 'POST':
        original = request.form.get('text_input', '')
        if original.strip():
            corrected = get_correction(original)
    return render_template('index.html', original=original, corrected=corrected)

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)