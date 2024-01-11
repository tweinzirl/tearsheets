# -*- coding: utf-8 -*-
"""
Created on Wed Jan 10 23:23:48 2024

@author: local_ergo
"""

import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning) 

if __name__ == '__main__':
    import tearsheet_utils as m
    docs = m.load_persona_html()
    vectordb = m.create_or_load_vectorstore('data/chroma', docs, override=True) #override=True)

    # test create_filter
    name = 'Jerry Smith'
    filter1 = m.create_filter(name, 'all')
    # filter2 = m.create_filter('Robert King', 'linkedin')
    # filter3 = m.create_filter('Robert King', ['linkedin', 'google'])
    # filter4 = m.create_filter('all', ['google'])

    # test Q&A for filters
    q1 = 'What is noteworthy about {name}?'
    q2 = f'where does {name} currently work?'
    q3 = 'What important roles does {name} have in the community?'
    q4 = 'Summarize all the recent news articles based on their titles'

    r1 = m.qa_metadata_filter(q1, vectordb, filter1)
    # r2 = m.qa_metadata_filter(q2, vectordb, filter1)
    # r3 = m.qa_metadata_filter(q3, vectordb, filter1)
    # r4 = m.qa_metadata_filter(q4, vectordb, filter1)