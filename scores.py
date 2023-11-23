import json, base64, hashlib, datetime, re
from textwrap import dedent
from typing import Optional

PATTERN = r"([_\*\[\]\(\)\\])"

FMT = r"%H:%M:%S - %d/%m/%Y"


def md_escape(input: Optional[str]) -> str:
    if input is None:
        return "Missing"

    return re.sub(PATTERN, r"\\\1", input)


def parse_name(input: Optional[str]) -> str:
    if input is None:
        return "Missing"

    name = input.strip()

    if len(name) > 200:
        return name[::200]

    return name


def parse_digest(input: Optional[str]) -> Optional[bytes]:
    if input is None:
        return

    digest = input.strip()

    try:
        digest_bytes = digest.encode("latin-1")
        decoded = base64.b64decode(digest_bytes)
        return decoded
    except:
        return


def digest_scores(input: list[float]) -> Optional[bytes]:
    try:
        values = ",".join("%.1f" % x for x in input)
        value_bytes = values.encode("latin-1")
        hash = hashlib.sha512(value_bytes)
        return hash.digest()
    except:
        return


def parse_scores(values: Optional[list[float | int]], count: int) -> list[float | int]:
    if values is None:
        raise ValueError("No values array provided")

    if len(values) != count:
        raise ValueError(f"Incorrect number of value scores provided: {len(values)}, expected {count}")

    for val in values:
        if not isinstance(val, (float, int)):
            raise TypeError(f"Invalid type of value: {val} ({type(val).__name__})")

        if val > 100 or val < 0:
            raise ValueError(f"Value ({val}) outside acceptable range (0-100)")

    return values


def parse_timestamp(timestamp: Optional[str]) -> Optional[datetime.datetime]:
    if timestamp is None:
        return

    time_str = timestamp.strip()

    try:
        return datetime.datetime.strptime(
            time_str,
            r"%Y-%m-%dT%H:%M:%S.%f%z"
        )
    except:
        pass


def check_edition(edition: Optional[str]) -> str:
    if isinstance(edition, str):
        edition = edition.strip().lower()

        if edition.startswith("s"):
            return "🤏 Short Edition"

        if edition.startswith("f"):
            return "🐍 Full Edition"

    return "❔ Missing Edition"


def check_digest(hash: Optional[bytes], scores: Optional[bytes]) -> str:
    if hash is None or scores is None:
        return "❓ Missing score authentication"

    if hash == scores:
        return "✅ Authentic score"
    else:
        return "❌ Tampered score"


class Scores:
    def __init__(self, data: dict, ua: Optional[str], count: int) -> None:
        # Name and scores
        self.name = parse_name(data.get("name"))
        self.scores = parse_scores(data.get("vals"), count)

        # Check authenticity
        score_digest = digest_scores(self.scores)
        sub_digest = parse_digest(data.get("digest"))
        self.authenticity = check_digest(score_digest, sub_digest)

        # Analytics (UA, version, time, edition, takes)
        self.ua = md_escape(ua)
        self.version = md_escape(data.get("version"))
        self.time = parse_timestamp(data.get("time"))
        self.edition = check_edition(data.get("edition"))

        takes: Optional[int] = data.get("takes")
        self.takes = "⁉️ Missing takes" if takes is None else str(takes)

    def to_code(self) -> str:
        data = {
            "name": self.name,
            "values": self.scores
        }

        sub_time = datetime.datetime.now(tz=datetime.timezone.utc)

        ans_time = "⏳ Missing time" if self.time is None else self.time.strftime(FMT)

        body = f'''
            **User:** {md_escape(self.name)}
            **Time Submitted:** {sub_time.strftime(FMT)} (UTC)
            **Time Answered:** {ans_time} (UTC)
            **Edition:** {self.edition}
            **Authenticity:** {self.authenticity}
            **Takes**: {self.takes}
            **User Agent:** {self.ua}
            **Version:** {self.version}
            ```json
            {{}}
            ```'''
        return dedent(body).format(
            json.dumps(data, sort_keys=True, indent=4)
        )


__all__ = [
    "Scores"
]
