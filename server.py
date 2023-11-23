import os
from typing import cast
from sys import version_info as vi
from quart import Quart, request
from quart_cors import cors, route_cors
from brotli_asgi import BrotliMiddleware, ASGIApp
from webhook import Webhook
from scores import Scores

raw_app = Quart(__name__)
app = cors(
    raw_app,
    allow_origin=["https://pcbvalues.github.io"]
)

asgi = cast(ASGIApp, app.asgi_app)
app.asgi_app = BrotliMiddleware(asgi)  # type: ignore

webhook = Webhook(os.getenv("URL", ""), os.getenv("PFP", ""))


@app.route("/")
async def index():
    return f'<h1 style="text-align: center;">Running on Python {vi.major}.{vi.minor}.{vi.micro}</h1>'


@app.post("/apiv3/")
@route_cors(
    allow_headers=["Content-Type"],
    allow_methods=["POST"],
    allow_origin=["https://pcbvalues.github.io"]
)
async def apiv3() -> tuple[dict[str, str | bool], int]:
    try:
        data = await request.get_json()
        scores = Scores(data, request.headers.get("User-Agent"), 7)
        await webhook.post(scores.to_code(), f"PCBValues - {scores.name}")
        return {"success": True}, 200

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }, 500

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)
