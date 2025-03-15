import pytest

from xivlodestone import LodestoneScraper
from xivlodestone.models import SimpleCharacter


@pytest.mark.asyncio
async def test_search_characters_by_name():
    """Test basic character search functionality"""
    lodestone = LodestoneScraper()

    characters = [c async for c in lodestone.search_characters("Yoshi'p Sampo")]
    assert len(characters) > 1

    for character in characters:
        assert isinstance(character, SimpleCharacter)
        assert character.id > 0
        assert character.first_name
        assert character.last_name
        assert character.name
        assert "Yoshi'p" in character.name
        assert character.world
        assert character.datacenter
        assert character.avatar_url
        assert character.lodestone_url
        assert character.lodestone_url.startswith(lodestone.CHARACTER_URL)
        assert str(character) == character.name


@pytest.mark.asyncio
async def test_search_characters_by_exact_name_and_world():
    """Test character search by name and world"""
    lodestone = LodestoneScraper()

    characters = [c async for c in lodestone.search_characters("Yoshi'p Sampo", "Mandragora")]
    assert len(characters) == 1
    assert characters[0].id == 13822072


@pytest.mark.asyncio
async def test_search_characters_limited():
    """Test character search with a limit"""
    lodestone = LodestoneScraper()

    characters = [c async for c in lodestone.search_characters("G'raha", limit=235)]
    for character in characters:
        assert character.id > 0
        assert character.first_name
        assert character.last_name
        assert character.world
        assert character.datacenter
        assert character.avatar_url
        assert character.lodestone_url
        assert character.lodestone_url.startswith(lodestone.CHARACTER_URL)

    assert len(characters) == 235


@pytest.mark.asyncio
async def test_search_characters_empty():
    """Test that empty search returns no results"""
    lodestone = LodestoneScraper()

    characters = [c async for c in lodestone.search_characters("_")]
    assert len(characters) == 0


# todo: test_search_free_companies
