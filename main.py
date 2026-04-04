import uvicorn
from src.core.app import app
from src.core.config import config


def main():
    uvicorn.run(app,
                host=config.app.HOST,
                port=config.app.PORT)


if __name__ == '__main__':
    main()
