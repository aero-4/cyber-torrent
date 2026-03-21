import uvicorn
from src.core.app import app


def main():
    uvicorn.run(app)


if __name__ == '__main__':
    main()