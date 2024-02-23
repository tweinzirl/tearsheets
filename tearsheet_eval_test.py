# -*- coding: utf-8 -*-
"""
Created on Wed Jan 10 23:23:48 2024

@author: local_ergo
"""

import tearsheet_utils as tu
import ragas.metrics as rag_m

import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning) 

# %%
if __name__ == '__main__':
    
    docs = tu.load_persona_html()
    vectordb = tu.create_or_load_vectorstore('data/chroma', docs, override=True) #override=True)

    name = 'Jerry Smith'
    filter1 = tu.create_filter(name, 'all')
    
    # test Q&A for filters
    q1 = 'What is noteworthy about {name}?'
    q2 = f'where does {name} currently work?'
    q3 = 'What important roles does {name} have in the community?'
    q4 = 'Summarize all the recent news articles based on their titles'

    r1 = tu.qa_metadata_filter(q1, vectordb, filter1, eval_metric = [rag_m.faithfulness, rag_m.answer_relevancy])
    # r2 = tu.qa_metadata_filter(q2, vectordb, filter1,
    #                             eval_metric = [rag_m.faithfulness, rag_m.answer_relevancy, rag_m.context_relevancy], eval_metric_viz = True)