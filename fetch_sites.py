"""Fetch one HTML page and return a consistent status/HTML record.

Checks robots.txt before requesting the page. SKIPPED means access could not
be verified or was disallowed; ERROR means the request failed.
A successful HTTP response is not proof that the page contains product data."""

import requests
from functools import lru_cache
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser

headers = {
        "User-Agent" : "EcommerceAuditAnalyzerBot/0.1"
    }

#STEP 1: Caching
@lru_cache(maxsize=32)

def get_robots(origin):
    try:
        response = requests.get(
            origin + "/robots.txt",
            headers=headers,
            timeout=(5, 8)
        )

        if response.status_code == 404:
            return None, None

        if response.status_code != 200:
            return None, "Could not verify robots.txt rules"

        robots = RobotFileParser()
        robots.parse(response.text.splitlines())

        return robots, None

    except requests.RequestException as error:
        return None, str(error)

# STEP 2: Normalize the requested URL and identify the crawler.
def fetch_site(url):
    url = url.strip()
    parsed = urlparse(url)

    # headers = {
    #     "User-Agent" : "EcommerceAuditAnalyzerBot/0.1"
    # }

    # # STEP 2: Check robots.txt; do not silently bypass access restrictions.
    # robots_url = urljoin(url, "/robots.txt")

    if parsed.scheme not in ("http", "https") or not parsed.hostname:
        return {
            "status": "ERROR",
            "message": "Invalid URL",
            "html": ""
        }

    origin = f"{parsed.scheme}://{parsed.netloc}"

    robots, error = get_robots(origin)

    if error:
        return {
            "status": "SKIPPED",
            "message": error,
            "html": ""
        }

    if robots is not None:
        if not robots.can_fetch(headers["User-Agent"], url):
            return {
                "status": "SKIPPED",
                "message": "Access disallowed by robots.txt",
                "html": ""
            }
    try:
        print("Downloading HTML:", url, flush=True)

        response = requests.get(
            url,
            headers=headers,
            timeout=(5, 10),
            allow_redirects=False
        )

        # robots_response = requests.get(
        #     headers=headers,
        #     timeout=(5, 10),
        #     allow_redirects=False
        # )

        if response.is_redirect:
            return {
                "status": "SKIPPED",
                "message": "Redirect requires separate robots.txt check",
                "html": ""
            }

        response.raise_for_status()

        return {
            "status": "OK",
            "message": "Page downloaded successfully",
            "html": response.text
        }

    except requests.RequestException as error:
        return {
            "status": "ERROR",
            "message": str(error),
            "html": ""
        }
