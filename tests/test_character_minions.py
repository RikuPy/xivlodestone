import pytest

from xivlodestone import LodestoneScraper


@pytest.mark.asyncio
async def test_get_character_minions():
    """Test fetching a character's minions"""
    lodestone = LodestoneScraper()

    minions = await lodestone.character_minions(13822072)
    assert len(minions) >= 3

    assert minions[0].name == "Wind-up G'raha Tia"
    assert minions[1].name == "Wind-up Herois"
    assert minions[2].name == "Wind-up Airship"

    for minion in minions:
        assert minion.icon_url