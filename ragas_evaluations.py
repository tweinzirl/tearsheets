# -*- coding: utf-8 -*-
"""
Created on Thu Jan 11 13:18:11 2024

@author: local_ergo
"""

# Evaluation
from ragas.metrics import *
from ragas.langchain import RagasEvaluatorChain # langchain chain wrapper to convert a ragas metric into a langchain

def ragas_eval_qa(result, eval_metrics_list = [faithfulness, answer_relevancy, context_relevancy]):

    # make eval chains
    eval_chains = {
        metric.name: RagasEvaluatorChain(metric=metric) 
        for metric in eval_metrics_list
    }  
    # metric_tracker = {}
    for metric, eval_chain in eval_chains.items():
        metric_name = f'{metric}_score'
        result[metric_name]= eval_chain({'query':q,
                                                 'source_documents':result['source_documents'],
                                                 'result':result['result']})[metric_name]
        return result