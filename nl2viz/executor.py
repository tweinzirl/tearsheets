import base64
import io
import traceback
from typing import Any, List
import matplotlib.pyplot as plt
import pandas as pd
from nl2viz.datamodel import ChartExecutorResponse, Summary
from nl2viz.utils import preprocess_code, get_globals_dict
import copy

class ChartExecutor:
    """Execute code and return chart object"""

    def __init__(self) -> None:
        pass

    def execute(
        self,
        code_specs: List[str],
        data: Any,
        library="matplotlib",
        return_error: bool = False,
    ) -> Any:
        """Validate and convert code"""

        charts = []
        code_spec_copy = copy.copy(code_specs)
        code_specs = [preprocess_code(code) for code in code_specs]
        if library == "matplotlib":
            for code in code_specs:
                try:
                    ex_locals = get_globals_dict(code, data)
                    # print(ex_locals)
                    exec(code, ex_locals)
                    chart = ex_locals["chart"]
                    if plt:
                        # hold the image data in the memory
                        buf = io.BytesIO()
                        plt.box(False)
                        plt.grid(color="lightgray", linestyle="dashed", zorder=-10)
                        plt.tight_layout()
                        # try:
                        #     plt.draw()
                        #     # plt.tight_layout()
                        # except AttributeError:
                        #     print("Warning: tight_layout encountered an error. The layout may not be optimal.")
                        #     pass

                        plt.savefig(buf, format="png", dpi=200, pad_inches=0)
                        buf.seek(0)
                        # now the conent of the buffer is (containig the image data) are read and encoded into base64 format in text form which can be used stored or transmitted over the web
                        plot_data = base64.b64encode(buf.read()).decode("ascii")
                        plt.close()
                    charts.append(
                        ChartExecutorResponse(
                            status=True,
                            raster=plot_data,
                            code=code,
                            library=library,
                        )
                    )
                except Exception as exception_error:
                    print(code_spec_copy[0])
                    print("****\n", str(exception_error))
                    #print(traceback.format_exc())
                    if return_error:
                        charts.append(
                            ChartExecutorResponse(
                                status=False,
                                raster=None,
                                code=code,
                                library=library,
                                error={
                                    "message": str(exception_error),
                                    "traceback": traceback.format_exc(),
                                },
                            )
                        )
            return charts
        else:
            raise Exception(
                f"Unsupported library. Only matplotlib library is supported."
            )
