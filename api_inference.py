import google.generativeai as genai

from google import genai
from groq import Groq

import time

# client = genai.Client(api_key=model_key)
# response = client.models.generate_content(
#     model=model_name,
#     contents=prompt
# )
# return response.text

def api_inference(chunk, model_name, model_type, model_key):
    from groq import Groq

    if model_type=="groq":
        prompt = "Extract the flashcards with front and back in given format from the given format. STRICTLY adhere to the format.\n The format is : Front::   \n Back::  \n The text is :  "+    chunk + "\nRespond directly with the front and back ONLY."
        client = Groq(api_key=model_key)
        response = client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    
    
    time.sleep(12) 
    client = genai.Client(api_key=model_key)
    max_retries = 5
    delay = 15 

    for attempt in range(max_retries):
        try:
            prompt = "Extract the flashcards with front and back in given format from the given format. STRICTLY adhere to the format.\n The format is : Front::   \n Back::  \n The text is :  " +    chunk + "\nRespond directly with the front and back ONLY.";

            response = client.models.generate_content(
                model = model_name,
                contents = prompt
            )
        except Exception as e:
            if "429" in str(e):
                print(f"Rate limited, waiting {delay}s before retry {attempt+1}/{max_retries}")
                time.sleep(delay)
                delay *= 2  
            else:
                raise e

    return response.text



