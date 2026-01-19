from services.youtube_embed import build_youtube_embed_url


def test_build_youtube_embed_url_watch():
    url = "https://www.youtube.com/watch?v=VIDEO123"
    embed = build_youtube_embed_url(url)
    assert embed == (
        "https://www.youtube.com/embed/VIDEO123"
        "?autoplay=1&mute=1&controls=0&rel=0&modestbranding=1&playsinline=1&enablejsapi=1"
    )


def test_build_youtube_embed_url_short():
    url = "https://youtu.be/VIDEO456"
    embed = build_youtube_embed_url(url)
    assert embed.startswith("https://www.youtube.com/embed/VIDEO456?")


def test_build_youtube_embed_url_embed():
    url = "https://www.youtube.com/embed/VIDEO789"
    embed = build_youtube_embed_url(url)
    assert embed.startswith("https://www.youtube.com/embed/VIDEO789?")


def test_build_youtube_embed_url_invalid():
    assert build_youtube_embed_url("https://example.com/video") is None
    assert build_youtube_embed_url("") is None
    assert build_youtube_embed_url(None) is None
