import pytest

from xivlodestone import LodestoneScraper
from xivlodestone.models import SimpleCharacter


@pytest.mark.asyncio
async def test_search_characters_by_name(lodestone: LodestoneScraper):
    """Test basic character search functionality"""
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
async def test_search_characters_by_exact_name_and_world(lodestone: LodestoneScraper):
    """Test character search by name and world"""
    characters = [c async for c in lodestone.search_characters("Yoshi'p Sampo", "Mandragora")]
    assert len(characters) == 1
    assert characters[0].id == 13822072


@pytest.mark.asyncio
async def test_search_characters_limited(lodestone: LodestoneScraper):
    """Test character search with a limit"""
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
async def test_search_characters_empty(lodestone: LodestoneScraper):
    """Test that empty search returns no results"""
    characters = [c async for c in lodestone.search_characters("_")]
    assert len(characters) == 0


# todo: test_search_free_companies
