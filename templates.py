from pathlib import Path

from starlette.templating import Jinja2Templates


path = Path("src/templates")
templates = Jinja2Templates(directory=path)
