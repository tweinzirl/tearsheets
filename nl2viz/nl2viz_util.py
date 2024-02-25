import os
from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv()) # read local .env file
import dbio
cobj = dbio.connectors.SQLite('data/db/synthetic_tran.db')

from nl2viz import manager as m
from nl2viz import openai_textgen
from nl2viz.datamodel import ChartExecutorResponse, Summary


def save_image(
        chart: ChartExecutorResponse,
        client_name:str, 
        chart_title: str
    ) -> str:

    client_name = client_name.replace(" ","_").upper()
    chart_title = chart_title.replace(" ","_")

    save_dir = "nl2viz_img" 
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    img_path = os.path.join(save_dir, f'{client_name}-{chart_title}.png')
    chart.savefig(img_path)

    return img_path


def vizgen(name: str = 'Robert King', question: str = 'what transactions are performed most often'):
    
    # read data 
    df = cobj.read(f'select * from transactions where Client_Name = \'{name}\'')

    # instantiate
    nlviz = m.Manager(text_gen=openai_textgen.TextGenerator(), data=df)

    # create summary 
    # TODO need to cache the summary so it'll be faster 
    # generate a summary of client after they select the client 
    # 
    llm_config = {"n":1, 'max_tokens':2000, "temperature": 0}
    summary = nlviz.summarize(
        textgen_config=llm_config,
        summary_method="default")

    # generate plot 
    charts = nlviz.visualize(summary=summary, goal=question, textgen_config=llm_config, return_error=True)

    # save image
    img_path = save_image(chart=charts[0], client_name=name, chart_title=question)

    return img_path, charts[0].code, Summary(**summary)


if __name__ == '__main__':
    vizgen()
