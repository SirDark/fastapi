import threading
from pathlib import Path
from converter import convertModelFiles
import asyncio


class BackgroundTask(threading.Thread):
    def __init__(self, input_path: Path, format: str, output_path: Path):
        super(BackgroundTask, self).__init__()
        self.input_path = input_path
        self.fileformat = format
        self.output_path = output_path

    def run(self) -> None:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        print("conversion started.")
        loop.run_until_complete(convertModelFiles(self.input_path, self.fileformat, self.output_path))
        loop.close()
        print("conversion completed.")
