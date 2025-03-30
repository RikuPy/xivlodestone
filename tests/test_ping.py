import pytest

from xivlodestone import LodestoneScraper


@pytest.mark.asyncio
async def test_ping():
    lodestone = LodestoneScraper()
    await lodestone.ping()
