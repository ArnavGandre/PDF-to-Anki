import re

def sanitize_output(text):

    if not text:
        print("No text provided to extract Q&A from")
        return {"pairs:": []}

    pairs = {"pairs": []}
    lines = text.split('\n')
    
    current_question = None
    current_answer = None

    front_pattern = r'^(?:Front::|Question:)\s*(.*?)$'
    back_pattern = r'^(?:Back::|Answer:)\s*(.*?)$'
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        question_match = re.match(front_pattern, line, re.IGNORECASE)
        if question_match:
            if current_question and current_answer:
                pairs["pairs"].append({
                    "front": current_question.strip(),
                    "back": current_answer.split("Note:")[0].strip()
                })
            current_question = question_match.group(1)
            current_answer = None
            continue
        
        answer_match = re.match(back_pattern, line, re.IGNORECASE)
        if answer_match:
            current_answer = answer_match.group(1)
        elif current_answer is not None:
            current_answer += " " + line
        elif current_question and not current_answer:
            current_answer = line
    
    if current_question and current_answer:
        pairs["pairs"].append({
            "front": current_question.strip(),
            "back": current_answer.strip()
        })
    
    return pairs
    