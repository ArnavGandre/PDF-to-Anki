import sentence_transformers
from sentence_transformers.util import cos_sim
import matplotlib.pyplot as plt
import numpy as np
import json
model = sentence_transformers.SentenceTransformer('all-MiniLM-L6-v2')

def semantic_chunk(sentences, sens):
    em = model.encode(sentences);
    print(em.shape);

    count = 0;
    dists = [];

    while count<em.shape[0]-1:

        dist = cos_sim(em[count], em[count+1]);
        
        dists.append(float(dist));
        
        count+=1;
    
    threshold = np.percentile(dists, sens)
    
    count = 0;
    chunks = []
    current_chunk = []


    for i, sentence in enumerate(sentences):
        current_chunk.append(sentence);
        if i < len(dists) and dists[i]< threshold:
            chunks.append(current_chunk);
            current_chunk = [];
    
    if current_chunk:
        chunks.append(current_chunk)

    merged = []
    for chunk in chunks:
        if len(chunk) < 3 and merged:
            merged[-1].extend(chunk)
        else:
            merged.append(chunk)
    chunks = merged

    for each in chunks:
        print("\n");
        print(each);
        print("\n");
    
    return chunks;
    


