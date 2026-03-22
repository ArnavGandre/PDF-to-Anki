import json

def json_data(chunks, filename):

    data = {
        "last_processed_chunk":0,
        "chunks":[
            
        ]
    }

    for i, chunk in enumerate(chunks):
        data["chunks"].append({
            "id": i+1,
            "chunk" : " ".join(chunk)
        })

    with open(filename + ".json", "w") as f:
        json.dump(data, f, indent=4)
        
    return True