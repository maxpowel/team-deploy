from bundles.command.app import app

options = {
    "load_files": "command"
}


def init():
    app.run()