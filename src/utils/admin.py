import shutil
import uuid
from pathlib import Path

from markupsafe import Markup
from starlette.datastructures import FormData


def format_photo(model, attribute, width: int = 50):
    path = getattr(model, attribute)
    if not path:
        return "Нет фото"

    url = f"/{path}" if not path.startswith("/") else path

    return Markup(
        f'<a href="{url}" target="_blank">'
        f'<img src="{url}" width="{width}" style="border-top: 1px solid #eee;" />'
        f'</a>'
    )


async def on_model_change_photo(data: FormData):
    file = data.get("avatar_image")

    if file and hasattr(file, "filename") and file.filename:
        upload_dir = Path("static/uploads")
        upload_dir.mkdir(parents=True, exist_ok=True)

        suffix = Path(file.filename).suffix
        filename = f"{uuid.uuid4()}{suffix}"
        full_path = upload_dir / filename

        with open(full_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        data["avatar_image"] = f"static/uploads/{filename}"

    elif not file or not hasattr(file, "filename"):
        data.pop("avatar_image", None)
