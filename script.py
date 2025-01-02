import re
import json
import os
import pdfplumber
import torch
from transformers import pipeline
import genanki
import random



# Load TinyLlama pipeline
pipe = pipeline(
    "text-generation",
    model="TinyLlama/TinyLlama-1.1B-Chat-v1.0",
    torch_dtype=torch.bfloat16,
    device_map=0
)

# Define the Anki note model
CHEMISTRY_MODEL = genanki.Model(
    random.randrange(1 << 30, 1 << 31),  # Random model ID
    'Chemistry QA Model',
    fields=[
        {'name': 'Question'},
        {'name': 'Answer'},
        {'name': 'PageNumber'},
    ],
    templates=[
        {
            'name': 'Chemistry Card',
            'qfmt': '{{Question}}',
            'afmt': '{{FrontSide}}<hr id="answer">{{Answer}}<br><br>Page: {{PageNumber}}',
        },
    ]
)

def load_or_create_qa_file(filename='qa_data.json'):
    """Load existing QA data or create new file with initial structure"""
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                print(f"Error reading {filename}, creating new file")
    
    initial_data = {
        "metadata": {
            "last_processed_page": 9,
            "total_pages_processed": 0,
            "total_questions": 0,
            "last_update": "",
            "last_anki_card_index": -1  # Track the last card added to Anki
        },
        "qa_pairs": []
    }
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(initial_data, f, indent=2, ensure_ascii=False)
    
    return initial_data

def create_or_load_deck():
    """Create a new Anki deck or load existing deck information"""
    return genanki.Deck(
        random.randrange(1 << 30, 1 << 31),  # Random deck ID
        'CHEMISTRY'
    )

def add_new_cards_to_deck(deck, qa_data):
    """Add new cards to the deck starting from the last processed index"""
    last_processed_index = qa_data["metadata"]["last_anki_card_index"]
    new_cards_added = 0

    for i, qa_pair in enumerate(qa_data["qa_pairs"][last_processed_index + 1:], start=last_processed_index + 1):
        note = genanki.Note(
            model=CHEMISTRY_MODEL,
            fields=[
                qa_pair["question"],
                qa_pair["answer"],
                str(qa_pair["page_number"])
            ]
        )
        deck.add_note(note)
        new_cards_added += 1
        qa_data["metadata"]["last_anki_card_index"] = i

    return new_cards_added

def save_deck(deck):
    """Save the Anki deck to a file"""
    genanki.Package(deck).write_to_file('OUTPUT.apkg')

def generate_questions(context):
    print("generating questions \n")
    messages = [
        {
            "role": "system",
            "content": "You are an AI bot used to extract question and answers from documents",
        },
        {
            "role": "user", 
            "content": "Extract the question and answers from this text as it is in given format. STRICTLY adhere to the format.\n The format is : Question 1  \n Answer 1 \n The text is :  " + context + "\nRespond directly with the question and answers ONLY."
        }
    ]
    prompt = pipe.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    outputs = pipe(prompt, max_new_tokens=512)
    return outputs[0]["generated_text"]

def break_down_page_into_parts(text, part_size=500):
    parts = []
    current_part = ""
    for sentence in text.split(". "):
        if len(current_part) + len(sentence) + 1 <= part_size:
            current_part += sentence + ". "
        else:
            parts.append(current_part.strip())
            current_part = sentence + ". "
    if current_part:
        parts.append(current_part.strip())
    return parts

def extract_assistant_responses(text):
    print("extracting questions \n")
    assistant_pattern = r"<\|assistant\|>(.*?)(?=<\|system\|>|<\|user\|>|$)"
    matches = re.findall(assistant_pattern, text, re.DOTALL)
    cleaned_responses = [response.strip() for response in matches if response.strip()]
    
    if cleaned_responses:
        print(cleaned_responses[0])
        return cleaned_responses[0]
    return None

def extract_questions_and_answers(text):
    if not text:
        print("No text provided to extract Q&A from")
        return {"qa_pairs": []}

    qa_dict = {"qa_pairs": []}
    lines = text.split('\n')
    
    current_question = None
    current_answer = None
    
    question_pattern = r'^(?:Question(?:\s*\d*)?:?\s*)(.*?)$'
    answer_pattern = r'^(?:Answer(?:\s*\d*)?:?\s*)(.*?)$'
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        question_match = re.match(question_pattern, line, re.IGNORECASE)
        if question_match:
            if current_question and current_answer:
                qa_dict["qa_pairs"].append({
                    "question": current_question.strip(),
                    "answer": current_answer.strip()
                })
            current_question = question_match.group(1)
            current_answer = None
            continue
        
        answer_match = re.match(answer_pattern, line, re.IGNORECASE)
        if answer_match:
            current_answer = answer_match.group(1)
        elif current_answer is not None:
            current_answer += " " + line
        elif current_question and not current_answer:
            current_answer = line
    
    if current_question and current_answer:
        qa_dict["qa_pairs"].append({
            "question": current_question.strip(),
            "answer": current_answer.strip()
        })
    
    return qa_dict

def save_qa_data(data, filename='qa_data.json'):
    """Save QA data with current timestamp"""
    from datetime import datetime
    data["metadata"]["last_update"] = datetime.now().isoformat()
    
    temp_filename = filename + '.tmp'
    with open(temp_filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    os.replace(temp_filename, filename)

def main():
    qa_data = load_or_create_qa_file()
    deck = create_or_load_deck()
    
    # Add any existing cards that haven't been added to Anki yet
    new_cards = add_new_cards_to_deck(deck, qa_data)
    if new_cards > 0:
        print(f"Added {new_cards} existing cards to Anki deck")
        save_deck(deck)
    
    start_page = qa_data["metadata"]["last_processed_page"] + 1
    print(f"Resuming from page {start_page}")
    
    try:
        with pdfplumber.open("YOUR_PDF_PATH) as pdf:
            total_pages = len(pdf.pages)
            
            if start_page >= total_pages:
                print("All pages have been processed!")
                return
            
            for page_num, page in enumerate(pdf.pages[start_page:], start_page):
                print(f"\nProcessing page {page_num} of {total_pages-1}")
                
                text = page.extract_text()
                if not text:
                    print(f"No text found on page {page_num}, skipping...")
                    continue
                
                print(f"Page length: {len(text)} characters")
                parts = break_down_page_into_parts(text)
                
                page_has_valid_qa = False
                
                for i, part in enumerate(parts):
                    print(f"\nProcessing part {i+1} of {len(parts)}")
                    try:
                        result = generate_questions(part)
                        response = extract_assistant_responses(result)
                        
                        if response:
                            qa_dict = extract_questions_and_answers(response)
                            
                            if qa_dict["qa_pairs"]:
                                # Add metadata to each QA pair
                                for qa_pair in qa_dict["qa_pairs"]:
                                    qa_pair["page_number"] = page_num
                                    qa_pair["part_number"] = i + 1
                                    qa_data["qa_pairs"].extend([qa_pair])
                                
                                page_has_valid_qa = True
                                print(f"Added {len(qa_dict['qa_pairs'])} new Q&A pairs")
                                
                                # Update metadata
                                qa_data["metadata"]["last_processed_page"] = page_num
                                qa_data["metadata"]["total_questions"] = len(qa_data["qa_pairs"])
                                
                                # Add new cards to Anki deck
                                new_cards = add_new_cards_to_deck(deck, qa_data)
                                if new_cards > 0:
                                    print(f"Added {new_cards} new cards to Anki deck")
                                    save_deck(deck)
                                
                                # Save progress after each successful part
                                save_qa_data(qa_data)
                                
                                print(f"Total Q&A pairs so far: {len(qa_data['qa_pairs'])}")
                            else:
                                print("No Q&A pairs extracted from response")
                        else:
                            print("No valid response to extract Q&A from")
                            
                    except Exception as e:
                        print(f"Error processing part {i+1}: {str(e)}")
                        continue
                
                if page_has_valid_qa:
                    qa_data["metadata"]["total_pages_processed"] += 1
                    save_qa_data(qa_data)
                
                # Save progress after each page
                qa_data["metadata"]["last_processed_page"] = page_num
                save_qa_data(qa_data)
                
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        save_qa_data(qa_data)
        raise
    
    finally:
        print("\nFinal Statistics:")
        print(f"Last processed page: {qa_data['metadata']['last_processed_page']}")
        print(f"Total pages processed: {qa_data['metadata']['total_pages_processed']}")
        print(f"Total Q&A pairs extracted: {qa_data['metadata']['total_questions']}")
        print(f"Total Anki cards created: {qa_data['metadata']['last_anki_card_index'] + 1}")

if __name__ == "__main__":
    main()  
