from kairo.cli.app import app, chat
import sys


if __name__ == "__main__":
    # Simple dispatch: allow `python main.py chat` to run the chat command
    if len(sys.argv) > 1 and sys.argv[1] == "chat":
        chat()
    else:
        app()