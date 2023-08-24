from fastapi import APIRouter, File, UploadFile, Form, HTTPException
from math import ceil
import aiofiles
from pathlib import Path
from backgroundTask import BackgroundTask

router = APIRouter(
    prefix="",
    tags=["conversion"],
    responses={404: {"description": "not found"}, 500: {"description": "internal server error"}, 200: {"message": "ok"}}
)

convertable_formats = ['step', 'iges', 'stl', 'obj', '.step', '.iges', '.stl', '.obj']
half = ceil(len(convertable_formats) / 2)


async def savefile(in_file):
    async with aiofiles.open("./files/"+in_file.filename, 'wb') as out_file:
        while content := in_file.file.read(8192):
              await out_file.write(content)


@router.post("/convert")
async def convert(uploadedfile: UploadFile = File(...), convertto: str = Form(...)):
    if not uploadedfile.filename.lower().endswith(".shapr"):
        raise HTTPException(status_code=400, detail="Only shapr files (.shapr) are allowed.")
    if not (convertto.lower() in convertable_formats):
        raise HTTPException(status_code=400, detail="conversion only supported to " + ' '.join(convertable_formats[half:]))
    await savefile(uploadedfile)
    backtask = BackgroundTask(Path("./files/"+uploadedfile.filename), convertto, Path("./files/"))
    backtask.start()
    return router.responses.get(200)

