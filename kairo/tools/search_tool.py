import os

from kairo.tools.base import Tool


class SearchTool(Tool):

    name = "search_code"

    description = "Search source files"

    def execute(self, query):

        matches = []

        for root, _, files in os.walk("."):

            for file in files:

                if not file.endswith(".py"):
                    continue

                path = os.path.join(root, file)

                try:

                    with open(
                        path,
                        "r",
                        encoding="utf-8"
                    ) as f:

                        content = f.read()

                        if query.lower() in content.lower():

                            matches.append(path)

                except Exception:
                    pass

        return {
            "query": query,
            "matches": matches
        }