from pydantic.dataclasses import dataclass
from typing import List, Optional, Any
import base64


@dataclass
class Message:
    role:str
    content:str


@dataclass
class LLMResponse:
    """Response from a Large Language Model"""

    text: List[Message]
    config: Any
    usage: Optional[Any] = None
    response: Optional[Any] = None # full response object


@dataclass
class Goal:
    """A visualization goal"""
    question: str
    visualization: str
    rationale: str
    index: Optional[int] = 0

    def _repr_markdown_(self):
        return f"""
### Goal {self.index}
---
**Question:** {self.question}

**Visualization:** `{self.visualization}`

**Rationale:** {self.rationale}
"""
    

@dataclass
class Persona:
    """A persona"""
    persona: str
    rationale: str

    def _repr_markdown_(self):
        return f"""
### Persona
---

**Persona:** {self.persona}

**Rationale:** {self.rationale}
"""


@dataclass
class Summary:
    """A summary of a dataset"""

    name: str
    file_name: str
    dataset_description: str
    field_names: List[Any]
    fields: Optional[List[Any]] = None

    def _repr_markdown_(self):
        field_lines = "\n".join([f"- **{name}:** {field}" for name,
                                field in zip(self.field_names, self.fields)])
        return f"""
## Dataset Summary

---

**Name:** {self.name}

**File Name:** {self.file_name}

**Dataset Description:**

{self.dataset_description}

**Fields:**

{field_lines}
"""


@dataclass
class ChartExecutorResponse:
    """Response from a visualization execution"""

    status: bool  # True if successful
    raster: Optional[str]  # base64 encoded image
    code: str  # code used to generate the visualization
    library: str  # library used to generate the visualization
    error: Optional[dict] = None  # error message if status is False

    def _repr_mimebundle_(self, include=None, exclude=None):
        bundle = {"text/plain": self.code}
        if self.raster is not None:
            bundle["image/png"] = self.raster
        return bundle

    def savefig(self, path):
        """Save the raster image to a specified path if it exists"""
        if self.raster:
            with open(path, 'wb') as f:
                f.write(base64.b64decode(self.raster))
        else:
            raise FileNotFoundError("No raster image to save")