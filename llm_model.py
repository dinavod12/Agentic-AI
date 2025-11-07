import os
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI,AzureOpenAIEmbeddings

load_dotenv()

llm = AzureChatOpenAI(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_version=os.getenv("OPEN_API_VERSION"),
    model="gpt-4o-mini",  
    azure_deployment=os.getenv("OPEN_AI_MODEL"), 
    api_key=os.getenv("OPENAI_API_KEY"),
    temperature=0.6
)

embedding = AzureOpenAIEmbeddings(    
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("OPENAI_API_KEY"),
    azure_deployment="Kaarthipoc-text-embedding-ada-002",
    api_version=os.getenv("OPEN_API_VERSION"),
    )



#response = llm.invoke("Write a Python function to reverse a string.")
#print(response.content)
