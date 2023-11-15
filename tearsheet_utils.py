# utilities for building tearsheets 
# syntax for metadata filters: https://github.com/langchain-ai/langchain/discussions/10537

import os
import glob
import openai

# langchain
from langchain.document_loaders import UnstructuredHTMLLoader
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.chat_models import ChatOpenAI
from langchain.chains import RetrievalQA

# authentication
from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv())


def create_or_load_vectorstore(path, documents=[],
    embedding_function=OpenAIEmbeddings(), override=False):
    '''
    Create or load vectorstore in the specified `path`. If the path exists,
    and `override` is False, the vectorstore is returned. If `path` does
    nor exist OR `override` is True, then the vectorstore is (re)created
    given the list `documents`. The provided `embedding_function` applies
    in either case.
    '''

    if os.path.exists(path) and override==False:  # use existing
        vectordb = Chroma(persist_directory=path,
            embedding_function=embedding_function)
    else:
        # clean out existing data
        for f in glob.glob(os.path.join(path, '**', '*.*'), recursive=True):
            os.remove(f)
        vectordb = Chroma.from_documents(documents, embedding_function,
            persist_directory=path)

    return vectordb


def qa_metadata_filter(q, vectordb, filter, top_k=10,
    llm=ChatOpenAI(model_name='gpt-3.5-turbo', temperature=0)):
    '''
    Perform Q&A given a question `q`, vectorstore `vectordb`, and language
    model `llm`. The `top_k` most relevant documents meeting the requirements
    in `filter` are considered.
    '''

    # embed filter in retriever
    retriever = vectordb.as_retriever(
        search_kwargs={"k": top_k,
                       "filter": filter,})

    # run qa chain with retriever
    qa_chain = RetrievalQA.from_chain_type(llm, retriever=retriever)
    result = qa_chain({"query": q})

    return result['result']


def create_filter(client_name='all', doc_types='all', logical_operator='$and'):
     '''
     Create a filter for a single client name and/or a list of one or more
     document types.  No filter is applied to a field when the input is 'all'.
     If both filters are present, they are combined with a logical AND or OR
     via `logical_operator`.
     '''

     client_filter, doc_filter = None, None

     if isinstance(client_name, str) and client_name != 'all':
         client_filter = {'client_name': {'$eq': client_name}}

     if doc_types != 'all': # doc filter
         if isinstance(doc_types, str):  # convert to list
             doc_types = [doc_types]

         doc_filter = {'doc_type': {'$in': doc_types}}
    
     values = [f for f in [client_filter, doc_filter] if f is not None]
     if len(values) > 1:
         filter_ = {logical_operator: values}  # combine with $and or $or
     else:
         filter_ = values[0]  # return single dictionary

     return filter_


def load_persona_html():
    '''
    Load HTML documents for synthetic personas all into one dataset.
    '''
    urls = glob.glob('data/text/*html')
    docs = []
    for url in urls:
        doc = UnstructuredHTMLLoader(url).load()
        # infer client name and add to metadata
        root = url.split('/')[-1]
        toks = root.split('_')
        client_name = toks[:-1]
        doc_type = toks[-1][:-5]
        # manually edit metadata
        doc[0].metadata['client_name'] = ' '.join(client_name)
        doc[0].metadata['doc_type'] = doc_type
        docs.extend(doc)

    return docs


def tearsheet_bio(client, vectordb,
    llm=ChatOpenAI(model_name='gpt-3.5-turbo', temperature=0)):
    '''
    Build tearsheet bio for a given `client`.

    TODO: decide which details currently in the bio are better placed
    in a summary table.
    '''

    output1 = tearsheet_bio_1(client, vectordb, llm)  # separate q&a
    output2 = tearsheet_bio_2(client, output1, llm)  # consolidate
    output3 = tearsheet_bio_3(output2, llm)  # polish text
    return output3


def tearsheet_bio_1(client, vectordb, llm=ChatOpenAI(model_name='gpt-3.5-turbo', temperature=0)):
    all_docs = create_filter(client, 'all')

    multi_doc_prompt_dict = {'1':
              {'q': 'what is the current position of {client}?',
               'f': create_filter(client, 'linkedin'),
              },

         '2':
             {'q': 'where did {client} work prior to the current position?',
              'f': all_docs,
             },

         '3':
             {'q': 'what boards does the {client} currently serve on? What boards did they previously serve on?',
              'f': create_filter(client, ['linkedin', 'relsci', 'pitchbook']),
             },

         '4': {'q': 'what education credentials does {client} have',
               'f': all_docs,
              },

         '5': {'q': 'describe the nature (industry, purpose) of the organization where {client} currently works',
               'f': all_docs,
              },

         '6': {'q': 'describe the philantropic activies of {client}',
               'f': all_docs,
              },

         '7': {'q': 'compare the net worth of {client} to that of their family',
               'f': all_docs,
              },

         '8': {'q': 'describe any deals where the {client} was a lead partner',
               'f': create_filter(client, 'pitchbook'),
              },

         '9': {'q': 'summarize the investment bio of {client}. Include the amounts of stock and options sold in the last 36 months.',
               'f': create_filter(client, ['equilar', 'pitchbook']),  # applying doc filter here gets more specific and response
              },

         '10': {'q': 'what stock did {client} sell and when were the effective dates?',
               'f': create_filter(client, 'equilar'),
              },

         '11': {'q': 'summarize recent news articles about {client}',
               'f': create_filter(client, 'google'),  # doc filter also makes difference here
              },
        }

    # answer each question separately
    for key in multi_doc_prompt_dict.keys():
        q = multi_doc_prompt_dict[key]['q'].format(client=client)
        f = multi_doc_prompt_dict[key]['f']
        response = qa_metadata_filter(q, vectordb, f, llm=llm)
        multi_doc_prompt_dict[key]['a'] = response

    return multi_doc_prompt_dict


def tearsheet_bio_2(client, qa_dict,
    llm=ChatOpenAI(model_name='gpt-3.5-turbo', temperature=0)):

    '''
    Given a client and a dictionary of Q&A responses, build a summary
    paragraph that according to the prompt embedded in this function.
    TODO: pass in the prompt as input.
    '''

    bio_prompt_template = '''
        You are a writer and biographer. You specialize in writing
        accurate life summarizes given large input documents.
        Below is information from several documents about a single
        client named {client}.

        Prepare a biography that includes in the following order:
        1. The client's name and estimated individual net worth
        2. Family net worth
        3. Their professional work history, deals as lead partner
        4. Summary of their investment activities and any recent stock or option sales
        5. Board member activities
        6. Philantropic activities
        7. Their education
        8. Recent news articles about the client

        Format the output as prose rather than an ordered list.
        Use matter of fact statements and avoid phrases like "According to ..."
        and "Unfortunately, there are no details about".

        If there are no details on a particular topic, then completely omit
        it from the response.

        Input context:
        {context}

        Your response here:
    '''

    context = ''
    for key in qa_dict:
        context += ('\n\n' + qa_dict[key]['a'])

    formatted_prompt = bio_prompt_template.format(client=client, context=context)

    response = llm.call_as_llm(formatted_prompt)

    return response


def tearsheet_bio_3(proposed_bio,
    llm=ChatOpenAI(model_name='gpt-3.5-turbo', temperature=0)):

    '''
    Reformat the output into a single paragraph and adjust language as
    specified in the input prompt.
    '''

    prompt = f'''Reformat the text below as a single paragraph, preserving order and details.\
    Remove any sentences conveying missing details or insufficient information. Do not include sentences starting witih words like "Unfortunately".

    ###
    {proposed_bio}
    ###

    Your response here:
    '''

    response = llm.call_as_llm(prompt)

    return response


if __name__ == '__main__':
    import tearsheet_utils as m
    docs = m.load_persona_html()
    vectordb = m.create_or_load_vectorstore('data/chroma', docs, override=False) #override=True)
    # test filter 1: require exact match for multiple fields w/ logical OR
    filter_ = {'$or': [{'client_name': {'$eq': 'Robert King'}},
            {'doc_type': {'$eq': 'linkedin'}}]}
    junk = vectordb.similarity_search('summarize the current employers of all people', k=99, filter=filter_)
    for d in junk: print(d.metadata)

    # test filter 2: match to lists of values with logical AND
    filter_ = {'$and': [{'client_name': {'$in': ['Robert King']}},
            {'doc_type': {'$in': ['linkedin', 'relsci', 'equilar']}}]}
    junk = vectordb.similarity_search('summarize the current employers of all people', k=99, filter=filter_)
    for d in junk: print(d.metadata)

    # test create_filter
    filter1 = m.create_filter('Robert King', 'all')
    filter2 = m.create_filter('Robert King', 'linkedin')
    filter3 = m.create_filter('Robert King', ['linkedin', 'google'])
    filter4 = m.create_filter('all', ['google'])

    # test Q&A for filters
    q1 = 'What is noteworthy about Robert King?'
    q2 = 'where does Robert King currently work?'
    q3 = 'What important roles does Robert King have in the community?'
    q4 = 'Summarize all the recent news articles based on their titles'

    r1 = m.qa_metadata_filter(q1, vectordb, filter1)
    r2 = m.qa_metadata_filter(q2, vectordb, filter2)
    r3 = m.qa_metadata_filter(q3, vectordb, filter3)
    r4 = m.qa_metadata_filter(q4, vectordb, filter4)

    # test tearsheet functions separately
    output1 = m.tearsheet_bio_1('Robert King', vectordb)
    output2 = m.tearsheet_bio_2('Robert King', output1)
    output3 = m.tearsheet_bio_3(output2)

    # test tearsheet bio
    bio1 = m.tearsheet_bio('Zeus Manly', vectordb)
    bio2 = m.tearsheet_bio('Velvet Throat', vectordb)
    bio3 = m.tearsheet_bio('Julia Harpman', vectordb)
