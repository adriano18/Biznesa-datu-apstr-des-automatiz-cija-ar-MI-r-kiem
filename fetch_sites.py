import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from urllib.robotparser import RobotFileParser

def fetch_site(url):
    url = url.strip()

    headers = {
        "User-Agent" : "EcommerceAuditAnalyzerBot/0.1"
    }

    robots_url = urljoin(url, "/robots.txt")

    try:
        robots_response = requests.get(
            robots_url,
            headers=headers,
            timeout=10
        )

        if robots_response.status_code == 200:
            robots = RobotFileParser()
            robots.parse(robots_response.text.splitlines())

            if not robots.can_fetch(headers["User-Agent"], url):
                return {
                    "status": "SKIPPED",
                    "message": "Access disallowed by robots.txt",
                    "html": ""
                }

        elif robots_response.status_code != 404:
            return {
                "status": "SKIPPED",
                "message": "Could not verify robots.txt rules",
                "html": ""
            }

        response = requests.get(
            url,
            headers=headers,
            timeout=15
        )

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
