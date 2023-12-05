# prototype chatbot withe four key functions:
# - generate tearsheet
# - query database and display data
# - query database and plot data
# - chat with vectorstore

# local imports
import tearsheet_utils as tshu
import email_utils as emut

# system imports
import os
import openai

from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv()) # read local .env file
openai.api_key = os.environ['OPENAI_API_KEY']

from langchain.agents import AgentExecutor
from langchain.agents.format_scratchpad import format_to_openai_functions
from langchain.agents.output_parsers import OpenAIFunctionsAgentOutputParser
from langchain.chat_models import ChatOpenAI
from langchain.memory import  ChatMessageHistory, ConversationBufferMemory
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.schema import AIMessage, HumanMessage
from langchain.schema.runnable import RunnablePassthrough
from langchain.tools import tool
from langchain.tools.render import format_tool_to_openai_function


from typing import Optional, List
from pydantic.v1 import BaseModel, Field

import gradio

# load vectordb
vectordb = tshu.create_or_load_vectorstore('data/chroma',
    tshu.load_persona_html(), 
    override=False)
 

# define chat_with_docs function
class ChatWithDocsInput(BaseModel):
    query: str = Field(..., description="Pass the entire user's question unaltered into this parameter.")
    client_name: str = Field(..., description="Name of client to query for.")

@tool(args_schema=ChatWithDocsInput)
def chat_with_docs(query: str,  client_name: str) -> dict:
    # question: should document details go here or in the chat agent prompt?
    """
    Search the document store with the given query for the given client name. 
    The document store filters for the top documents given the query. Document
    types include:
    
    'equilar' - For details on stock or equity transactions, stock sold, annual compensation.
    'google' - For recent news articles listed on google.
    'linkedin' - For employment history, education, board memberships, and bio.
    'pitchbook' - For deals as lead partner, investor bio.
    'relsci' - For current or prior board memberships, top donations.
    'wealthx' - For individual and family net worth, interests, passions, hobbies.
    """

    client_name = ' '.join([w.capitalize() for w in client_name.split(' ')])

    # create filter and run query
    filter_ = tshu.create_filter(client_name, 'all')
    print(query, filter_)
    response = tshu.qa_metadata_filter(query, vectordb, filter_, top_k=5)

    #return f'called chat_with_docs for client {client_name}' #response
    return response


# define generate_and_send_tearsheet function
class GenSendTearsheetInput(BaseModel):
    client_name: str = Field(..., description="Name of client to generate tearsheet for.")
    email: str = Field(..., description="Email that will receive tearsheet this function sends.")

@tool(args_schema=GenSendTearsheetInput)
def gen_send_tearsheet(client_name: str, email: str) -> dict:
    """
    Generate the tearsheet for the given client_name. Send to the given email
    address. If the tearsheet already exists, it is read from disk rather than
    freshly remade.
    """

    client_name = ' '.join([w.capitalize() for w in client_name.split(' ')])

    # generate
    html, output_path = tshu.generate_tearsheet(client_name, vectordb, override=False)

    # todo: format / send email
    msg, success = emut.send_message(html, f'Your Tearsheet For {client_name}', email, verbose=False)

    return f'called gen_send_tearsheet for client {client_name} and recipient {email}: {success}' #response

# what clients do I have?
@tool
def list_my_clients() -> dict:
    """
    Look up all the client names according to metadata in the global vectorstore.
    """

    md = vectordb.get()['metadatas']
    return list(set([doc['client_name'] for doc in md]))



# define table_from_db

# define plot_from_db

# define custom agent as class
class ChatAgent:
    '''Custom agent for using tools defined in this module.'''

    def __init__(self):
        # update this list of tools as more are added
        tools = [chat_with_docs, gen_send_tearsheet, list_my_clients]
        openai_functions = [format_tool_to_openai_function(f) for f in tools]

        # prompt
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are helpful but sassy assistant"),
            MessagesPlaceholder(variable_name="chat_history"),
            ("user", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ])

        # model
        model = ChatOpenAI(temperature=0).bind(functions=openai_functions)

        # memory
        memory = ConversationBufferMemory(return_messages=True, memory_key="chat_history")
        
        # agent chain
        agent_chain = RunnablePassthrough.assign(
            agent_scratchpad= lambda x: format_to_openai_functions(x["intermediate_steps"])
        ) | prompt | model | OpenAIFunctionsAgentOutputParser()


        self.agent = AgentExecutor(agent=agent_chain, tools=tools, verbose=True, memory=memory)

    def run(self, user_input):
        '''Function that submits user input to chatbot.'''

        response = self.agent.invoke({"input": user_input})
        #repsonse is a dict with keys for input, output, chat_history

        return response['output']


if __name__ == '__main__':
    import chatbot1 as m

    """
    # todo: check right documents retrieved with simple query
    # invent llm call to tag question with document types and use those as
    # part of chat_with_docs: nested llm calls
    # response: yes, this is working correctly, verified with
    # vectordb.similarity_search and filter = {'client_name': 'Robert King'}

    tools = [m.chat_with_docs, m.gen_send_tearsheet]
    functions = [m.format_tool_to_openai_function(f) for f in tools]
    model = m.ChatOpenAI(temperature=0).bind(functions=functions)
    prompt = m.ChatPromptTemplate.from_messages([
        ("system", "You are helpful but sassy assistant"),
        ("user", "{input}"),
    ])
    chain = prompt | model | m.OpenAIFunctionsAgentOutputParser()

    # map tool names to callables 
    tool_map = {
        "chat_with_docs": m.chat_with_docs, 
        "gen_send_tearsheet": m.gen_send_tearsheet,
        }

    # test that questions map to the right functions
    # eval output with resultN.log
    result1 = chain.invoke({"input": "where does Robert King work?"})
    result2 = chain.invoke({"input": "what is Robert King's family net worth?"})
    result3 = chain.invoke({"input": "What deals as lead partner did Robert King do?"})
    result4 = chain.invoke({"input": "What recent news is there about Robert King?"})
    result5 = chain.invoke({"input": "Write a tearsheet about Robert King and send it to tweinzirl@gmail.com"})
    result6 = chain.invoke({"input": "Write a tearsheet about Julia Harpman and send it to tweinzirl@gmail.com"})
    result7 = chain.invoke({"input": "Write a tearsheet about Velvet Throat and send it to tweinzirl@gmail.com"})
    result8 = chain.invoke({"input": "Write a tearsheet about Jared Livinglife and send it to tweinzirl@gmail.com"})

    for i, result in enumerate([result1, result2, result3, result4, result5, result6, result7, result8]):
        observation = tool_map[result.tool].run(result.tool_input)
        print(f'\n{i}, {result.log} : {observation}\n')
    """

    # chatbot interface
    agent = m.ChatAgent()

    def agent_chat(query, history):
        '''
        Function to link gradio chat interface with langchain agent.
        Agent history is customized to match the chat history of the chat.
        This allows separate chats to take place simultaneously.
        Code based on https://www.gradio.app/guides/creating-a-chatbot-fast#a-langchain-example
        '''
        message_history = []
        for human, ai in history:
            message_history.append(HumanMessage(content=human))
            message_history.append(AIMessage(content=ai))

        agent.agent.memory.chat_memory = ChatMessageHistory(messages=message_history)

        return agent.run(query)


    demo = gradio.ChatInterface(fn=agent_chat,
        examples=["Where does CLIENT work?", "Send the tearsheet for CLIENT to EMAIL", "Who are my clients?"],
        title="Tearsheet Chatbot v0.1",
        retry_btn=None,
        undo_btn=None,
        clear_btn=None,
        )
    ### 
    demo.launch()


    #### todo: 
    #   1) update prompt in qa chain to always use the ocntext and ignore objections over not having access to personal information or recent news on google.
    # e.g., what is julia harpman doing these days?
    # - does julia harpman own any stock yet?

    # 2) email transcript of chat, may require agent as global variable

    # 3) customize dimensions, style of chatbot

    # good questions:
    #   - 'summarize Robert King\'s board membership history. separate current from prior positions. format as a markdown table'
    #   - list deals where client robert king has been lead partner
    #     -- who was robert king representing in that deal
    #     -- what was the size of the deal
    #     -- what is the status of the deal
    #     -- what other partners were involved in the deal

    #   - tell me about Velvet Throat's music career
