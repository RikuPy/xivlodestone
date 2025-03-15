import pytest

from xivlodestone import LodestoneScraper


@pytest.mark.asyncio
async def test_get_character_mounts():
    """Test fetching a character's mounts"""
    lodestone = LodestoneScraper()

    mounts = await lodestone.character_mounts(13822072)
    assert len(mounts) >= 13

    assert mounts[0].name == "Company Chocobo"
    assert mounts[1].name == "Chocobo Carriage"

    for mount in mounts:
        assert mount.icon_url