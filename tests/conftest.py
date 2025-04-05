import pytest

from xivlodestone import LodestoneScraper


@pytest.fixture
async def lodestone():
    return LodestoneScraper()
