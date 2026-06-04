import os

from kairo.tools.base import Tool


class SearchTool(Tool):

    name = "search_code"

    description = "Search for text in source files"

    def execute(self, query):

        results = []

        for root, _, files in os.walk("."):

            for file in files:

                if file.endswith(".py"):

                    path = os.path.join(root, file)

                    with open(path, "r", encoding="utf-8") as f:

                        content = f.read()

                        if query.lower() in content.lower():

                            results.append(path)

        return results