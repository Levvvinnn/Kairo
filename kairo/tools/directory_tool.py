from pathlib import Path

from kairo.tools.base import Tool


class DirectoryTool(Tool):

    name = "list_directory"

    description = "Lists files and folders"

    def execute(self, path="."):

        p = Path(path)

        if not p.exists():
            return {"error": "Directory not found"}

        return {
            "path": str(p),
            "entries": [
                str(item)
                for item in p.iterdir()
            ]
        }