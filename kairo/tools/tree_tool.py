from pathlib import Path

from kairo.tools.base import Tool


class FileTreeTool(Tool):

    name = "get_file_tree"

    description = "Returns a recursive project file tree"

    def execute(self, path="."):

        p = Path(path)

        tree = []

        for item in p.rglob("*"):

            if ".git" in str(item):
                continue

            if ".venv" in str(item):
                continue

            tree.append(str(item))

        return {
            "tree": tree
        }