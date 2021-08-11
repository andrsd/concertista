import os
import platform


class Assets:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls, *args, **kwargs)
            cls._instance.on_new()
        return cls._instance

    def on_new(self):
        if platform.system() == "Darwin":
            path = os.environ.get('RESOURCEPATH', os.path.dirname(__file__))
        else:
            path = os.path.dirname(__file__)

        self.music_dir = os.path.join(path, 'music')
        self.icons_dir = os.path.join(path, 'icons')
