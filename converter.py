from pathlib import Path
import time
import shutil


async def convertModelFiles(input_path: Path, pformat: str, output_path: Path):
    status = 0
    while status < 100:
        time.sleep(1.5)
        status += 10
        print(str(status) + "%")
    filename = (str(input_path).split('/')[-1].split('.')[0]) + pformat
    shutil.copy(input_path, filename)
    print("converted")


