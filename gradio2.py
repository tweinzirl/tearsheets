# simple gradio app to test display of html and plots

import gradio
import argparse
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def update_html(size=(10,)):
    '''Generate random dataframe'''

    df = {'A': np.random.randint(-10, 10, size=size),
          'B': np.random.randint(-30, -10, size=size),
          'C': np.random.randint(10, 999, size=size),
          }

    return pd.DataFrame(df).to_html(index=False)


def update_plot():
    '''Generate plot of random sinc function'''

    damping = 1/np.random.randint(1, 20)
    x = np.arange(-10, 10, 0.1)
    y = damping * np.sin(x)/x
    fig = plt.figure(figsize=(5,5))
    ax = fig.add_subplot(111)
    plt.plot(x, y, 'ko', ms=2)
    plt.plot(x, y, 'k-')
    plt.ylim(y.min(), y.max())

    return fig


if __name__ == '__main__':

    # argument handler
    parser = argparse.ArgumentParser(description='Start app. Optionally share to web.')
    parser.add_argument('--share', dest='share', action='store_true',
                        help='Share the app to the web (default: False).')

    args = parser.parse_args()
    print(args)

    with gradio.Blocks() as demo:
        # checkbox group
        with gradio.Row(equal_height=True):
            b1 = gradio.Button("Update HTML")
            b2 = gradio.Button("Update PLOT")

        # output stored as list: HTML and PLOT widgets
        with gradio.Row(equal_height=True):
            out_html = gradio.HTML('Placeholder')
            out_plot = gradio.Plot()

        b1.click(update_html, None, [out_html])
        b2.click(update_plot, None, [out_plot])
        
    demo.launch(share=args.share)
