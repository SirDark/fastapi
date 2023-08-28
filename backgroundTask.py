import subprocess
import threading
import models
from databasehandler import get_db


class BackgroundTask(threading.Thread):
    def __init__(self, input_path: str, pformat: str, output_path: str, dbid):
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

        strcommand = "python -u .\\files\\converter.py " + self.input_path + " " + self.fileformat + " " + self.output_path

        # print(strcommand)

        process = subprocess.Popen(strcommand, stdout=subprocess.PIPE, universal_newlines=True, bufsize=1)
        while True:
            line = process.stdout.readline()
            conversion_model.status = "in progress " + line.strip()
            db.add(conversion_model)
            db.commit()
            if not line:
                break

        print("conversion completed.")

        conversion_model.status = "Done"
        db.add(conversion_model)
        db.commit()
