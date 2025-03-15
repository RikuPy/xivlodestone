import logging

import aiohttp

from xivlodestone.errors import LodestoneError, NotFoundError


class BaseScraper:
    def __init__(self):
        self._logger = logging.getLogger()

    async def _fetch_page(self, url: str, *, mobile: bool = False) -> str:
        """
        Downloads the HTML output of a given URL.

        Args:
            url (str): The URL to fetch.
            mobile (bool): Sets a mobile user agent if True. The mobile lodestone website has
                a different layout than the desktop version, and makes scraping easier on some
                pages, but more difficult on others.

        Returns:
            str: The HTML content of the page.

        Raises:
            LodestoneError: If an error occurs while fetching the page.
            NotFoundError: If the requested resource could not be found (404).
        """
        self._logger.debug(f"Fetching page as {'mobile' if mobile else 'desktop'}: {url}")
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Mobile Safari/537.3"
                if mobile
                else "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36"
            )
        }

        try:
            async with aiohttp.ClientSession(headers=headers) as session:
                async with session.get(url) as response:
                    if response.status != 200:
                        if response.status == 404:
                            raise NotFoundError("The requested resource could not be found", url)
                        raise LodestoneError(
                            f"Received a {response.status} error from the Lodestone", url
                        )
                    return await response.text()
        except LodestoneError:
            raise
        except Exception as e:
            raise LodestoneError(e) from e

    @staticmethod
    def _get_attr(element, attr) -> str | None:
        """
        Retrieves an attribute from an element and ensures it's a string.

        Args:
            element: The element to retrieve the attribute from.
            attr: The attribute name to retrieve.

        Returns:
            str | None: The attribute value, or None if not found.
        """
        value = element.get(attr)
        if isinstance(value, list):
            return value[0]

        return value
