from multiprocessing import context

import torch
from transformers import pipeline

MODEL_CONFIGS = {
    "tinyllama": {
        "hf_id": "TinyLlama/TinyLlama-1.1B-Chat-v1.0",
        "system_prompt": "You are a helpful assistant.",
        "template": "tinyllama"
    },
    "phi3": {
        "hf_id": "microsoft/Phi-3-mini-4k-instruct",
        "system_prompt": "You are a helpful assistant.",
        "template": "phi3"
    }
}

_pipe = None

def load_model(model_name, model_path=None):
    global _pipe
    config = MODEL_CONFIGS[model_name]
    model_to_load = model_path if model_path else config["hf_id"]
    _pipe = pipeline(
        "text-generation",
        model=model_to_load,
        dtype=torch.bfloat16,
        device_map=0
    )

def local_inference (chunk, model_name, model_path=None):
    global _pipe
    if _pipe is None:
        load_model(model_name, model_path)

    messages = [
        {
            "role": "system",
            "content": "You are an AI bot used to extract flashcards from documents",

        },
        {
            "role": "user",
            # "content": "Extract the flashcards with front and back in given format from the given format. STRICTLY adhere to the format.\n The format is : Front::   \n Back::  \n The text is :  "+    chunk + "\nRespond directly with the front and back ONLY."
            "content": "Extract the question and answers from this text as it is in given format adhere to the format.\n The format is : Question: \n Answer: \n The text is :  " + chunk + "\nRespond directly with the question and answers ONLY."


        }
    ]
    prompt = _pipe.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    outputs = _pipe(prompt, max_new_tokens=512)
    raw = outputs[0]["generated_text"]
    torch.cuda.empty_cache()
    print("RAW OUTPUT:", raw)  # add this
    return outputs[0]["generated_text"]
