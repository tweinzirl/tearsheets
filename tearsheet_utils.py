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

