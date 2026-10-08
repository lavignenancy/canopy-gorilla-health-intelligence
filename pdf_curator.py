def curate_knowledge_base(pdf_metadata_list):
    curated_list = []
    for doc in pdf_metadata_list:
        title = doc['title'].lower()
        content_sample = doc['sample_text'].lower()
        
        if any(term in title or term in content_sample for term in ['e-cigarette', 'lipoprotein', 'lyme', 'neandertal']):
            continue
            
        if 'gorilla' in content_sample or 'respiratory' in content_sample or 'zoonotic' in content_sample:
            if 'captive' in content_sample or 'eaza' in title or 'aza' in title:
                doc['curated_category'] = "Captive Management Protocol (Zoonotic Only)"
            else:
                doc['curated_category'] = "Primary Mountain Gorilla Field Manual"
            curated_list.append(doc)
            
    return curated_list
