from urllib.parse import parse_qs, urlparse


EMBED_PARAMS = "autoplay=1&mute=1&controls=0&rel=0&modestbranding=1&playsinline=1&enablejsapi=1"


def build_youtube_embed_url(youtube_url: str | None) -> str | None:
    if not youtube_url:
        return None
    url = youtube_url.strip()
    if not url:
        return None

    try:
        parsed = urlparse(url)
    except ValueError:
        return None

    host = parsed.netloc.lower()
    path = parsed.path.strip("/")
    video_id = None

    if "youtu.be" in host:
        if path:
            video_id = path.split("/")[0]
    elif "youtube.com" in host:
        if path == "watch":
            video_id = parse_qs(parsed.query).get("v", [None])[0]
        else:
            parts = path.split("/")
            if len(parts) >= 2 and parts[0] == "embed":
                video_id = parts[1]

    if not video_id:
        return None

    return f"https://www.youtube.com/embed/{video_id}?{EMBED_PARAMS}"
