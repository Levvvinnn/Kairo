from kairo.tools.base import Tool
from pathlib import Path


class ProjectAnalyzerTool(Tool):

    name = "analyze_project"

    description = "Analyze a Python project"

    def execute(self, path="."):

        files = []

        for item in Path(path).rglob("*.py"):
            files.append(str(item))

        return {
            "python_files": files
        }