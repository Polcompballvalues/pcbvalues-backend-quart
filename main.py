import asyncio
from hypercorn.config import Config
from hypercorn.asyncio import serve
from server import app


def main() -> None:
    config = Config()
    config.bind = ["0.0.0.0"]
    asyncio.run(serve(app, config))


if __name__ == "__main__":
    main()
