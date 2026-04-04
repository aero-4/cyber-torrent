from markupsafe import Markup


def format_image_url(model, attribute):
    return Markup(f'<img src="{getattr(model, attribute)}"/>')