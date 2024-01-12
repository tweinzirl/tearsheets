# -*- coding: utf-8 -*-
"""
Created on Thu Jan 11 13:18:11 2024

@author: local_ergo
"""

# Evaluation
from ragas.metrics import *
from ragas.langchain import RagasEvaluatorChain # langchain chain wrapper to convert a ragas metric into a langchain
import matplotlib.pyplot as plt

def ragas_eval_qa(query, result, eval_metrics_list = [faithfulness, answer_relevancy, context_relevancy], viz = False):

    # make eval chains
    eval_chains = {
        m.name: RagasEvaluatorChain(metric=m) 
        for m in eval_metrics_list
    }  
    
    for metric, eval_chain in eval_chains.items():
        metric_name = f'{metric}_score'
        result[metric_name]= eval_chain({'query':query,
                                                 'source_documents':result['source_documents'],
                                                 'result':result['result']})[metric_name]
    # Bar plot of the metrics 
    if viz:
        plot_metric = {k:result[k] for k in [metric.name + '_score' for metric in eval_metrics_list]}
        plot_metrics_with_values(plot_metric, title = 'RAGAS Metrics')
        
    return result


def plot_metrics_with_values(metrics_dict, title='RAG Metrics'):
    """
    Plots a bar chart for metrics contained in a dictionary and annotates the values on the bars.
    Args:
    metrics_dict (dict): A dictionary with metric names as keys and values as metric scores.
    title (str): The title of the plot.
    """
    names = list(metrics_dict.keys())
    values = list(metrics_dict.values())
    plt.figure(figsize=(10, 6))
    bars = plt.barh(names, values, color='skyblue')
    # Adding the values on top of the bars
    for bar in bars:
        width = bar.get_width()
        plt.text(width + 0.01,  # x-position
                 bar.get_y() + bar.get_height() / 2,  # y-position
                 f'{width:.4f}',  # value
                 va='center')
    plt.xlabel('Score')
    plt.title(title)
    plt.xlim(0, 1)  # Setting the x-axis limit to be from 0 to 1
    plt.show()
    
    
if __name__ == '__main__':
    import ragas_evaluations as m
    
    m.plot_metrics_with_values({'faithfulness_score': 1.0,
                              'answer_relevancy_score': 0.9468557283238227,
                              'context_relevancy_score': 0.025}, "Base Retriever ragas Metrics")