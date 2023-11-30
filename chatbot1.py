# prototype chatbot withe four key functions:
# - generate tearsheet
# - query database and display data
# - query database and plot data
# - chat with vectorstore

# local imports
import tearsheet_utils as tshu

# system imports
import os
import openai

from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv()) # read local .env file
openai.api_key = os.environ['OPENAI_API_KEY']

from langchain.tools import tool
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.tools.render import format_tool_to_openai_function
from langchain.agents.output_parsers import OpenAIFunctionsAgentOutputParser

from typing import Optional, List
from pydantic.v1 import BaseModel, Field

# define chat_with_docs function
class ChatWithDocsInput(BaseModel):
    query: str = Field(..., description="Question to ask the document store.")
    client_name: str = Field(..., description="Name of client to query for.")
    doc_types: Optional[List[str]] = Field(default=['all'], description="Types of documents to search for.")

@tool(args_schema=ChatWithDocsInput)
def chat_with_docs(query: str,  client_name: str, doc_types: list=['all']) -> dict:
    # question: should document details go here or in the chat agent prompt?
    """
    Query the document store for the given client name. Optionally specify a
    list of document types. If document types not specified, then all documents
    are used. Supported document types include:
    
    'all' - Search all documents
    'equilar' - For details on stock or equity transactions, stock sold, annual compensation.
    'google' - For recent news articles listed on google.
    'linkedin' - For employment history, education, board memberships, and bio.
    'pitchbook' - For deals as lead partner, investor bio.
    'relsci' - For current or prior board memberships, top donations.
    'wealthx' - For individual and family net worth, interests, passions, hobbies.
    """

    # decide which documents to search
    if 'all' in doc_types:
        filter_docs = 'all'
    else:
        filter_docs = doc_types

    # create filter and run query
    filter_ = tshu.create_filter(client_name, filter_docs)
    #response = tshu.qa_metadata_filter(query, vectordb, filter_)

    return 'called chat_with_docs' #response


# define generate_tearsheet function
# include is the client_name and recipient email address
# function wraps around tshu.generate_tearsheet(client, vectordb)

# define table_from_db

# define plot_from_db

#tools = [get_current_temperature, search_wikipedia]

if __name__ == '__main__':
    import chatbot1 as m
    m.chat_with_docs('where does robert work?', 'Robert King', ['linkedin'])
