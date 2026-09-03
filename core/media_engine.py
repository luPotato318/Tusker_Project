import json
import os
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen

from django.core.cache import cache


CATEGORY_TERMS = {
    "tecnologia": "technology students coding industry 4.0",
    "indústria 4.0": "industry 4.0 robotics automation",
    "gestão": "business management young professionals",
    "oratória": "public speaking presentation students",
    "liderança": "young leadership teamwork",
    "entrevista de emprego": "job interview young professional",
}


def _normalized_query(query):
    lowered = (query or "educação profissional").strip().lower()
    for key, value in CATEGORY_TERMS.items():
        if key in lowered:
            return value
    return query or "students professional education"


def _get_json(url, headers=None, timeout=4):
    request = Request(url, headers={"User-Agent": "PIEM-Tusker-Power/3.1", **(headers or {})})
    with urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode())


def get_contextual_image(query, orientation="landscape"):
    """Busca Unsplash, cai para Pexels e mantém fallback parametrizado sem quebrar a UI."""
    search = _normalized_query(query)
    cache_key = f"piem:image:v1:{orientation}:{search}".lower().replace(" ", "-")
    cached = cache.get(cache_key)
    if cached:
        return cached

    unsplash_key = os.getenv("UNSPLASH_ACCESS_KEY", "")
    if unsplash_key:
        params = urlencode({"query": search, "orientation": orientation, "per_page": 1})
        try:
            payload = _get_json(
                f"https://api.unsplash.com/search/photos?{params}",
                {"Authorization": f"Client-ID {unsplash_key}"},
            )
            url = payload["results"][0]["urls"]["regular"]
            cache.set(cache_key, url, 86400)
            return url
        except (KeyError, IndexError, OSError, ValueError):
            pass

    pexels_key = os.getenv("PEXELS_API_KEY", "")
    if pexels_key:
        params = urlencode({"query": search, "orientation": orientation, "per_page": 1})
        try:
            payload = _get_json(
                f"https://api.pexels.com/v1/search?{params}",
                {"Authorization": pexels_key},
            )
            url = payload["photos"][0]["src"]["large2x"]
            cache.set(cache_key, url, 86400)
            return url
        except (KeyError, IndexError, OSError, ValueError):
            pass

    fallback = f"https://source.unsplash.com/1600x900/?{quote(search)}"
    cache.set(cache_key, fallback, 3600)
    return fallback
