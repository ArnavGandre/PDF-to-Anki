from sentence_extract import extract_sentences
from chunker import semantic_chunk
from json_maker import json_data
from api_inference import api_inference
from sanitize_output import sanitize_output
from local_inference import local_inference, load_model
from anki_maker import anki_maker

import json
import pdfplumber


model_names=[
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant",
]

def run_pipeline(pdf_path, chunk_sens, json_filename, json_output_filename, api_key, model_name_offdevice, model_type, model_name_ondevice, is_local, deck_name):
        

    def extract_text_from_pdf(pdf_path):
        with pdfplumber.open(pdf_path) as pdf:
            text = ''
            for page in pdf.pages:
                text += " " + page.extract_text()
        return text

    text = extract_text_from_pdf(pdf_path)

    sentences = extract_sentences(text)

    chunks = semantic_chunk(sentences, chunk_sens)

    json_data(chunks, json_filename)

    all_pairs = []

    if is_local:
        load_model(model_name_ondevice)

    with open(json_filename + ".json", "r") as json_file:
        data = json.load(json_file)

    for chunk_obj in data["chunks"]:
        if chunk_obj["id"] <= data["last_processed_chunk"]:
            continue
        chunk_text = chunk_obj["chunk"]
        
        if is_local:
            output = local_inference(chunk_text, model_name_ondevice)
        else:
            output = api_inference(chunk_text, model_name_offdevice, model_type, api_key)
        
        fb_pairs = sanitize_output(output)
        all_pairs.extend(fb_pairs["pairs"])
        data["last_processed_id"] = chunk_obj["id"]
        with open("data.json", "w") as f:
            json.dump(data, f, indent=4)

    with open(json_output_filename + ".json", "w") as f:
        json.dump({"pairs": all_pairs}, f, indent=4)

    anki_maker(all_pairs, deck_name, json_output_filename)

    return json_output_filename + ".apkg"