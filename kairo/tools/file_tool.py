from pathlib import Path

from kairo.tools.base import Tool


class FileTool(Tool):

    name = "read_file"

    description = "Read a local file"

    def execute(self, path: str):

        file_path = Path(path)

        if not file_path.exists():
            return {"error": "File not found"}

        return {
            "path": str(file_path),
            "content": file_path.read_text()
        }