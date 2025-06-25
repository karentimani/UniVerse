import json
from pathlib import Path
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.schema import Document
from langchain.embeddings import HuggingFaceEmbeddings
import torch


with open("mix.json", "r", encoding="utf-8") as f:
    data = json.load(f)

flat_chunks = []  

def add_chunk(title, content, metadata_extra=None):
    """Append a chunk only if content is non-empty"""
  
    if isinstance(content, list) and not content:
        return
    if isinstance(content, str) and not content.strip():
        return
    if isinstance(content, list):
        content = "\n".join(content)
    if not isinstance(content, str):
        content = str(content)
    metadata = {"source": title}
    if metadata_extra:
        metadata.update(metadata_extra)
    flat_chunks.append({
        "text": f"{title}\n{content}",
        "metadata": metadata
    })


for uni in data.get("universities", []):
    uni_name = uni.get("university_name")
    if not uni_name:
        continue  
    uni_meta = {"university": uni_name}

    
    for section_key, section_title in [
        ("university_name", "Name"),
        ("university_link", "Website"),
        ("locations", "Locations"),
        ("about", "About"),
        ("admission_requirements", "Admission Requirements"),
        ("tuition_fee_general_information", "Tuition Info"),
        ("Undergraduate_Financial_Aid", "Undergrad Financial Aid"),
        ("Applying_for_financial_aid", "Applying for Financial Aid"),
    ]:
        if section_key in uni and uni.get(section_key):
            add_chunk(f"{uni_name} - {section_title}", uni.get(section_key), {**uni_meta, "section": section_key})


    for faculty in uni.get("faculties", []):
        fac_name = faculty.get("name") or faculty.get("faculty_name")
        if not fac_name:
            continue  
        fac_meta = {**uni_meta, "faculty": fac_name}


        for major in faculty.get("majors", []):
            major_name = major.get("name")
            if not major_name:
                continue  
            major_meta = {**fac_meta, "major": major_name}
            prefix = f"{uni_name} | Faculty: {fac_name} | Major: {major_name}"

            add_chunk(f"{prefix} - Name", major_name, {**major_meta, "section": "major_name"})

            for m_key, m_sec in [
                ("overview", "Overview"),
                ("credits_distributed", "Credits Distribution"),
                ("courses", "Courses"),
                ("fees", "Fees"),
                ("years_of_study", "Years of Study"),
                ("location", "Location"),
            ]:
                if major.get(m_key):
                    add_chunk(f"{prefix} - {m_sec}", major.get(m_key), {**major_meta, "section": m_key})

        
        for minor in faculty.get("minors", []):
            minor_name = minor.get("name")
            if not minor_name:
                continue  
            minor_meta = {**fac_meta, "minor": minor_name}
            prefix = f"{uni_name} | Faculty: {fac_name} | Minor: {minor_name}"
            for m_key, m_sec in [("overview", "Overview"), ("courses", "Courses")]:
                if minor.get(m_key):
                    add_chunk(f"{prefix} - {m_sec}", minor.get(m_key), {**minor_meta, "section": m_key})


output_path = Path("flattened_chunks.json")
with output_path.open("w", encoding="utf-8") as out:
    json.dump(flat_chunks, out, ensure_ascii=False, indent=2)
print(f"✅ Saved processed chunks to {output_path}")

splitter = RecursiveCharacterTextSplitter(
    chunk_size=2000,
    chunk_overlap=300,
    separators=["\n\n", "\n", ".", " "]
)
all_docs = []
chunk_id = 0
for item in flat_chunks:
    text = item["text"]
    meta = item["metadata"]
    splits = splitter.split_text(text)
    for s in splits:
        all_docs.append(Document(page_content=s, metadata={**meta, "chunk_id": chunk_id}))
        chunk_id += 1


with open("chunks.json", "w", encoding="utf-8") as f:
    json.dump([
        {"content": doc.page_content, "metadata": doc.metadata}
        for doc in all_docs
    ], f, ensure_ascii=False, indent=2)
print("✅ Saved final split chunks to final_chunks.json")

print(f"✅ Total LangChain chunks: {len(all_docs)}")

embeddings = HuggingFaceEmbeddings(
    model_name="BAAI/bge-large-en-v1.5",
    encode_kwargs={"normalize_embeddings": True}
)
vectorstore = FAISS.from_documents(all_docs, embeddings)
vectorstore.save_local("last_vectorstore")
print("✅ Vectorstore saved to 'multi_unis_vectorstore'")
