from llm_model import embedding
from langchain_community.vectorstores.faiss import FAISS
#from langchain_core.vectorstores import Chroma
#from langchain_community.vectorstores import FAISS
#import langchain_community.vectorstores
from langchain_text_splitters import RecursiveCharacterTextSplitter
from chain_agent import read_brd_md
from chain_agent import read_brd_md
from langchain_text_splitters import RecursiveCharacterTextSplitter, MarkdownHeaderTextSplitter


"""def create_vector_store(md_texts):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=800)
    texts = text_splitter.create_documents([md_texts])
    #vectordb = Chroma.from_documents(documents=texts, embedding=embedding,persist_directory="./chroma_db")
    persist_path="./faiss_db_airfare"
    vectordb = FAISS.from_documents(documents=texts, embedding=embedding)
    vectordb.save_local(persist_path)
    return vectordb

def load_vector_store():
    vectordb = FAISS.load_local("./faiss_db_airfare",embeddings=embedding,allow_dangerous_deserialization=True)
    return vectordb

#RAG

def retrieve_similar_documents(query, k):
    vectordb = load_vector_store()
    results = vectordb.similarity_search_with_score(query, k=k)
    lst = []
    for i, (doc, score) in enumerate(results, 1):
        dict_data = {"score":f"{score:.4f}","docs":doc.page_content}
        lst.append(dict_data)
    return lst """


def build_chunks_with_metadata(md_texts: str):
    header_splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=[
            ("#", "h1"),
            ("##", "h2"),
            ("###", "h3"),
        ]
    )
    header_docs = header_splitter.split_text(md_texts)

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1500, 
        chunk_overlap=250,
        separators=["\n### ", "\n## ", "\n# ", "\n\n", "\n", ". "],  
        add_start_index=True,
    )

    chunks = []
    for d in header_docs:
        section = d.metadata.get("h1", None)
        subsection = d.metadata.get("h2", None)
        subsub = d.metadata.get("h3", None)
        for ch in text_splitter.create_documents([d.page_content]):
            meta = ch.metadata or {}
            meta.update({
                "section": section,
                "subsection": subsection or subsub,
                "start_index": meta.get("start_index"),
                "has_table": ("|" in ch.page_content) or ("- " in ch.page_content and "Code" in ch.page_content)
            })
            ch.metadata = meta
            chunks.append(ch)
    return chunks

#from langchain_community.vectorstores.faiss import FAISS
#from llm_model import embedding  

PERSIST_PATH = "./faiss_db_updated_All"

def create_vector_store(md_texts: str):
    docs = build_chunks_with_metadata(md_texts)
    vectordb = FAISS.from_documents(documents=docs, embedding=embedding)
    vectordb.save_local(PERSIST_PATH)
    return vectordb

def load_vector_store():
    vectordb = FAISS.load_local(PERSIST_PATH, embeddings=embedding, allow_dangerous_deserialization=True)
    return vectordb



def retrieve_similar_documents(query: str, k: int):
    vectordb = load_vector_store()
    results = vectordb.similarity_search_with_score(query, k=k)
    lst = []
    for i, (doc, score) in enumerate(results, 1):
        dict_data = {"score":f"{score:.4f}","docs":doc.page_content}
        lst.append(dict_data)
    return lst



#md_text = " "
#for i in range(2,35):
#    md_text+=read_brd_md(fr"C:\Users\2436230\OneDrive - Cognizant\Desktop\python\brd_main_steps_nested\markdown\mainstep_{i}.md")
#    md_text+="\n"

#create_vector_store(md_text)
