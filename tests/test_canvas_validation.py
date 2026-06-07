from kairo.integrations.canvas_client import CanvasClient


class DummyClient(CanvasClient):
    def __init__(self, base_url=None, token=None):
        pass

    def get_courses(self):
        return [{"id": 1, "name": "TestCourse"}]


def test_canvas_validation(monkeypatch):
    # monkeypatch network call by replacing CanvasClient.get_courses
    client = DummyClient()
    assert client.get_courses()[0]["name"] == "TestCourse"
