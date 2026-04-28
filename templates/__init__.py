from pathlib import Path

from starlette.templating import Jinja2Templates


BASE_DIR = Path(__file__).resolve().parents[1]
path = Path("templates")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


