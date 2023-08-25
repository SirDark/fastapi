import threading
from pathlib import Path
from converter import convertModelFiles
import asyncio
import models
from databasehandler import get_db


class BackgroundTask(threading.Thread):
    def __init__(self, input_path: Path, pformat: str, output_path: Path, dbid):
        super(BackgroundTask, self).__init__()
        self.input_path = input_path
        self.fileformat = pformat
        self.output_path = output_path
        self.dbid = dbid

    def run(self) -> None:
        db = next(get_db())
        conversion_model = db.query(models.Conversions).filter(models.Conversions.id == self.dbid).first()
        if conversion_model is None:
            print("conversion id is not in database")
            return
        conversion_model.status = "in progress"
        db.add(conversion_model)
        db.commit()

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        print("conversion started.")
        loop.run_until_complete(convertModelFiles(self.input_path, self.fileformat, self.output_path))
        loop.close()
        print("conversion completed.")

        conversion_model.status = "Done"
        db.add(conversion_model)
        db.commit()
