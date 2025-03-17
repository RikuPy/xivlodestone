import pytest

from xivlodestone import LodestoneScraper
from xivlodestone.enums import JobRole
from xivlodestone.errors import NotFoundError
from xivlodestone.models import Character, CharacterGrandCompany


@pytest.mark.asyncio
async def test_get_character():
    """Test fetching a character by ID"""
    lodestone = LodestoneScraper()

    character = await lodestone.get_character(13822072)
    assert isinstance(character, Character)
    assert isinstance(character.id, int)
    assert (
        character.lodestone_url == "https://na.finalfantasyxiv.com/lodestone/character/13822072/"
    )
    assert character.id == 13822072
    assert character.first_name == "Yoshi'p"
    assert character.last_name == "Sampo"
    assert character.world == "Mandragora"
    assert character.datacenter == "Meteor"
    assert character.avatar_url.startswith(
        "https://img2.finalfantasyxiv.com/f/a42d4c4183b08c329efcdb88991b1fac_ee738654add55c3d07ea92d8e108074cfc0.jpg"
    )
    assert character.title is None
    assert character.portrait_url.startswith(
        "https://img2.finalfantasyxiv.com/f/a42d4c4183b08c329efcdb88991b1fac_ee738654add55c3d07ea92d8e108074cfl0.jpg"
    )
    assert character.bio  == ""
    assert character.gender == "female"
    assert character.race == "Lalafell"
    assert character.clan == "Dunesfolk"
    assert character.birthday == "1st Sun of the 1st Astral Moon"
    assert character.guardian == "Halone, the Fury"
    assert character.city_state == "Ul'dah"
    assert isinstance(character.grand_company, CharacterGrandCompany)
    assert character.grand_company.name == "Immortal Flames"
    assert character.grand_company.rank == "Flame Captain"
    assert character.free_company is None
    assert character.level == 100
    assert character.jobs
    assert len(character.jobs) == 33

    for job in character.jobs:
        assert job.name
        assert job.icon_url
        assert job.role != JobRole.UNKNOWN


@pytest.mark.asyncio
async def test_character_not_found():
    """Test fetching a character that does not exist"""
    lodestone = LodestoneScraper()

    with pytest.raises(NotFoundError):
        await lodestone.get_character(56709)