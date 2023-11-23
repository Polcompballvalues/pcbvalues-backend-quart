import aiohttp


class Webhook:
    url: str
    pfp: str

    def __init__(self, url: str, pfp: str) -> None:
        self.url = url
        self.pfp = pfp

    async def check(self) -> None:
        async with aiohttp.ClientSession() as session:
            async with session.head(self.url) as resp:
                if resp.status > 299:
                    raise Exception("Webhook url not reachable")

    async def post(self, text="", title="") -> None:
        data = {
            "content": text,
            "username": title,
            "avatar_url": self.pfp
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(self.url, json=data) as resp:
                if resp.status > 299:
                    raise Exception("Failed to send scores to webhook")
