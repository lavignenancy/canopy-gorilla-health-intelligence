import pandas as pd
import os

def curate_knowledge_base_from_file(file_path="kb_documents.csv"):
    if not os.path.exists(file_path):
        return []
    
    df = pd.read_csv(file_path)
    raw_pdf_list = df.to_dict(orient='records')
    
    blacklist = ['e-cigarette', 'lipoprotein', 'lyme', 'neandertal']
    curated_knowledge = []
    seen_titles = set()
    
    for doc in raw_pdf_list:
        title = str(doc['title']).lower()
        text = str(doc['sample_text']).lower()
        
        if title in seen_titles:
            continue
        if any(term in title or term in text for term in blacklist):
            continue
            
        if 'gorilla' in text or 'respiratory' in text or 'zoonotic' in text:
            seen_titles.add(title)
            if 'captive' in text or 'eaza' in title or 'aza' in title:
                doc['curated_category'] = "Captive Management Protocol (Zoonotic Only)"
            else:
                doc['curated_category'] = "Primary Mountain Gorilla Field Manual"
            curated_knowledge.append(doc)
            
    return curated_knowledge
