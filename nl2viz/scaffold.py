from nl2viz.datamodel import Goal


class ChartScaffold:
    """Code scaffold for charts"""
    def __init__(self) -> None:
        pass

    def get_template(self, goal: Goal, library: str = 'matplotlib'):
        general_instructions = f"If the solution requires a single value (e.g. max, min, median, first, last etc), ALWAYS add a line (axvline or axhline) to the chart, ALWAYS with a legend containing the single value (formatted with 0.2F). If using a <field> where semantic_type=date, YOU MUST APPLY the following transform before using that column i) convert date fields to date types using data[''] = pd.to_datetime(data[<field>], errors='coerce'), ALWAYS use  errors='coerce' ii) drop the rows with NaT values data = data[pd.notna(data[<field>])] iii) convert field to right time format for plotting.  ALWAYS make sure the x-axis labels are legible (e.g., rotate when needed). Solve the task carefully by completing ONLY the <imports> AND <stub> section. Given the dataset summary, the plot(data) method should generate a {library} chart ({goal.visualization}) that addresses this goal: {goal.question}. DO NOT WRITE ANY CODE TO LOAD THE DATA. The data is already loaded and available in the variable data."

        matplotlib_instructions = f" {general_instructions} DO NOT include plt.show(). The plot method must return a matplotlib object (plt). Think step by step. \n"

        if library == "matplotlib":
            instructions = {
                "role": "assistant",
                "content": f"  {matplotlib_instructions}. Use BaseMap for charts that require a map. "}
            template = \
                f"""
import matplotlib.pyplot as plt
import pandas as pd
<imports>
# plan -
def plot(data: pd.DataFrame):
    <stub> # only modify this section
    plt.title('{goal.question}', wrap=True)
    return plt;

chart = plot(data) # data already contains the data to be plotted. Always include this line. No additional code beyond this line."""
        else:
            raise ValueError("Unsupported library. Only 'matplotlib' is supported.")
        return template, instructions
