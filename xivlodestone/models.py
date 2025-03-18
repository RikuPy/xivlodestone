# ruff: noqa: E501
from datetime import datetime
from typing import Literal, Annotated

from msgspec import Meta, Struct

from xivlodestone.enums import JobRole

__all__ = [
    "SimpleCharacter",
    "SimpleFreeCompany",
    "CharacterGrandCompany",
    "CharacterJob",
    "CharacterStats",
    "CharacterMinion",
    "CharacterMount",
    "CharacterFacewear",
    "Character",
    "FreeCompany",
]

name_pattern = r"^[a-zA-Z'\-]+$"
character_url_pattern = r"^https://na\.finalfantasyxiv\.com/lodestone/character/\d+/?"
fc_url_pattern = r"^https://na\.finalfantasyxiv\.com/lodestone/freecompany/\d+/?$"
img_cdn_pattern = r"^https://(lds-)?img\d?\.finalfantasyxiv\.com/[a-zA-Z\d\/\._\-?&]+$"


class SimpleCharacter(Struct, kw_only=True):
    """
    Provides basic character information found on search result pages and free company overviews.

    Attributes:
        id (int): The character's ID.
        lodestone_url (str): The URL to the character's Lodestone page.
        first_name (str): The character's first name.
        last_name (str): The character's last name.
        world (str): The character's world.
        datacenter (str): The character's datacenter.
        avatar_url (str): The URL to the character's avatar image.
    """

    id: int
    lodestone_url: Annotated[str, Meta(pattern=character_url_pattern)]
    first_name: Annotated[str, Meta(min_length=2, max_length=15, pattern=name_pattern)]
    last_name: Annotated[str, Meta(min_length=2, max_length=15, pattern=name_pattern)]
    world: Annotated[str, Meta(min_length=2, max_length=40, pattern=name_pattern)]
    datacenter: Annotated[str, Meta(min_length=2, max_length=40, pattern=name_pattern)]
    avatar_url: Annotated[str, Meta(pattern=img_cdn_pattern)]

    @property
    def name(self):
        """The players full character name."""
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return self.name


class SimpleFreeCompany(Struct, kw_only=True):
    """
    Provides basic free company information.

    Attributes:
        id (int): The free company's ID.
        lodestone_url (str): The URL to the free company's Lodestone page.
        name (str): The name of the free company.
        crest_component_urls (list[str]): List of URLs to the free company's crest components. Crest images are served
            in individual shapes and parts, in the same way that crests are designed in-game. You will need to
            stack these images together to form a full crest image for use in your application.
    """

    id: int
    lodestone_url: Annotated[str, Meta(pattern=fc_url_pattern)]
    name: Annotated[str, Meta(min_length=1, max_length=100)]
    crest_component_urls: list[Annotated[str, Meta(pattern=img_cdn_pattern)]]

    def __str__(self):
        return self.name


class CharacterGrandCompany(Struct, kw_only=True):
    """
    Provides the character's grand company name and rank.

    Attributes:
        name (str): The name of the grand company.
        rank (str): The rank of the character within the grand company.
    """

    name: Annotated[str, Meta(min_length=1, max_length=100)]
    rank: Annotated[str, Meta(min_length=1, max_length=100)]

    def __str__(self):
        return self.name


class CharacterJob(Struct, kw_only=True):
    """
    Provides the character's job or class information

    Attributes:
        name (str): The name of the class or job. Defaults to a job name if the character has unlocked their job,
            otherwise it will return a class name.
        level (int): The level of the class or job.
        icon_url (str): The URL to the icon image for the class or job.
        role (JobRole): The role of the class or job.
    """

    name: Annotated[str, Meta(min_length=1, max_length=100)]
    level: Annotated[int, Meta(ge=0, le=32767)]
    icon_url: Annotated[str, Meta(pattern=img_cdn_pattern)]
    role: JobRole

    def __str__(self):
        return self.name
    
    
class CharacterStats(Struct, kw_only=True):
    """
    Provides the character's stats information.

    Attributes:
        job_type (str): The type of job the player was last seen as (combat, gathering, or crafting).
        strength (int): The character's strength.
        dexterity (int): The character's dexterity.
        vitality (int): The character's vitality.
        intelligence (int): The character's intelligence.
        mind (int): The character's mind.
        critical_hit_rate (int): The character's critical hit rate.
        determination (int): The character's determination.
        direct_hit_rate (int): The character's direct hit rate.
        defense (int): The character's defense.
        magic_defense (int): The character's magic defense.
        attack_power (int): The character's attack power.
        skill_speed (int): The character's skill speed.
        attack_magic_potency (int | None): The character's attack magic potency, if they are on a combat job.
        healing_magic_potency (int | None): The character's healing magic potency, if they are on a combat job.
        spell_speed (int | None): The character's spell speed, if they are on a combat job.
        tenacity (int | None): The character's tenacity, if they are on a combat job.
        piety (int | None): The character's piety, if they are on a combat job.
        craftsmanship (int | None): The character's craftsmanship, if they are on a crafting job.
        control (int | None): The character's control, if they are on a crafting job.
        gathering (int | None): The character's gathering, if they are on a gathering job.
        perception (int | None): The character's perception, if they are on a gathering job.
        hp (int): The character's HP.
        mp (int | None): The character's MP, if they are on a combat job.
        cp (int | None): The character's CP, if they are on a crafting job.
        gp (int | None): The character's GP, if they are on a gathering job.
    """
    job_type: Literal["combat", "gathering", "crafting"]

    # Attributes
    strength: Annotated[int, Meta(ge=1, le=8388607)]
    dexterity: Annotated[int, Meta(ge=1, le=8388607)]
    vitality: Annotated[int, Meta(ge=1, le=8388607)]
    intelligence: Annotated[int, Meta(ge=1, le=8388607)]
    mind: Annotated[int, Meta(ge=1, le=8388607)]
    
    # Offensive Properties
    critical_hit_rate: Annotated[int, Meta(ge=1, le=8388607)]
    determination: Annotated[int, Meta(ge=1, le=8388607)]
    direct_hit_rate: Annotated[int, Meta(ge=1, le=8388607)]
    
    # Defensive Properties
    defense: Annotated[int, Meta(ge=1, le=8388607)]
    magic_defense: Annotated[int, Meta(ge=1, le=8388607)]
    
    # Physical Properties
    attack_power: Annotated[int, Meta(ge=1, le=8388607)]
    skill_speed: Annotated[int, Meta(ge=1, le=8388607)]
    
    # Mental Properties
    attack_magic_potency: Annotated[int, Meta(ge=1, le=8388607)] | None
    healing_magic_potency: Annotated[int, Meta(ge=1, le=8388607)] | None
    spell_speed: Annotated[int, Meta(ge=1, le=8388607)] | None
    
    # Role
    tenacity: Annotated[int, Meta(ge=0, le=8388607)] | None
    piety: Annotated[int, Meta(ge=0, le=8388607)] | None

    # Crafting
    craftsmanship: Annotated[int, Meta(ge=1, le=8388607)] | None
    control: Annotated[int, Meta(ge=1, le=8388607)] | None

    # Gathering
    gathering: Annotated[int, Meta(ge=1, le=8388607)] | None
    perception: Annotated[int, Meta(ge=1, le=8388607)] | None

    # Health / etc.
    hp: Annotated[int, Meta(ge=1, le=8388607)]
    mp: Annotated[int, Meta(ge=1, le=8388607)] | None
    cp: Annotated[int, Meta(ge=1, le=8388607)] | None
    gp: Annotated[int, Meta(ge=1, le=8388607)] | None


class CharacterMinion(Struct, kw_only=True):
    """
    Provides basic information about a character's minion.

    Attributes:
        name (str): The name of the minion.
        icon_url (str): The URL to the icon image for the minion.
    """

    name: Annotated[str, Meta(min_length=1, max_length=100)]
    icon_url: Annotated[str, Meta(pattern=img_cdn_pattern)]

    def __str__(self):
        return self.name


class CharacterMount(Struct, kw_only=True):
    """
    Provides basic information about a character's mount.

    Attributes:
        name (str): The name of the mount.
        icon_url (str): The URL to the icon image for the mount.
    """

    name: Annotated[str, Meta(min_length=1, max_length=100)]
    icon_url: Annotated[str, Meta(pattern=img_cdn_pattern)]

    def __str__(self):
        return self.name


class CharacterFacewear(Struct, kw_only=True):
    """
    Provides basic information about a character's facewear.

    Attributes:
        name (str): The name of the facewear.
        icon_url (str): The URL to the icon image for the facewear.
    """

    name: Annotated[str, Meta(min_length=1, max_length=100)]
    icon_url: Annotated[str, Meta(pattern=img_cdn_pattern)]

    def __str__(self):
        return self.name


class Character(SimpleCharacter, kw_only=True):
    """
    Provides detailed character information.

    Attributes:
        title (str | None): The character's title.
        portrait_url (str): The URL to the character's portrait image.
        bio (str | None): A bio written on the character's lodestone page, if they've provided one..
        gender (str): The character's gender.
        race (str): The character's race.
        clan (str): The character's clan or tribe.
        nameday (str): The character's nameday (in-game birthday).
        guardian (str): The character's guardian.
        city_state (str): The character's city-state.
        grand_company (CharacterGrandCompany | None): The character's grand company information.
        free_company (SimpleFreeCompany | None): The free company the character is a member of.
        level (int): The character's current level.
        jobs (list[CharacterJob]): A list of the character's jobs/classes.
    """

    title: Annotated[str, Meta(min_length=1, max_length=100)] | None = None
    portrait_url: Annotated[str, Meta(pattern=img_cdn_pattern)]
    bio: Annotated[str, Meta(max_length=3000)] = ""
    gender: Literal["male", "female"]
    race: Annotated[str, Meta(min_length=1, max_length=100)]
    clan: Annotated[str, Meta(min_length=1, max_length=100)]
    nameday: Annotated[str, Meta(min_length=1, max_length=100)]
    guardian: Annotated[str, Meta(min_length=1, max_length=100)]
    city_state: Annotated[str, Meta(min_length=1, max_length=100)]
    grand_company: CharacterGrandCompany | None = None
    free_company: SimpleFreeCompany | None = None
    level: Annotated[int, Meta(ge=1, le=32767)]
    jobs: list[CharacterJob]
    current_job: CharacterJob | None = None
    stats: CharacterStats


class FreeCompany(SimpleFreeCompany, kw_only=True):
    """
    Provides detailed free company information.

    Attributes:
        lodestone_url (str): The URL to the free company's Lodestone page.
        grand_company (str): The name of the grand company.
        name (str): The name of the free company.
        world (str): The world the free company is located in.
        datacenter (str): The datacenter the free company is located in.
        slogan (str): The free company's slogan.
        tag (str): The free company's tag without the « and » symbols.
        formed (datetime): The date the free company was formed.
        member_count (int): The number of members in the free company.
        rank (int): The rank of the free company.
        estate_name (str | None): The name of the free company's estate.
        estate_address (str | None): The address of the free company's estate.
        weekly_ranking (int | None): The free company's weekly ranking.
        monthly_ranking (int | None): The free company's monthly ranking.
        greeting (str | None): A greeting message from the free company.
        active (str): The activity status of the free company.
        recruiting (bool): Whether the free company is recruiting new members or not.
    """

    lodestone_url: Annotated[str, Meta(pattern=fc_url_pattern)]
    grand_company: Annotated[str, Meta(min_length=1, max_length=100)]
    name: Annotated[str, Meta(min_length=1, max_length=100)]
    world: Annotated[str, Meta(min_length=2, max_length=40, pattern=name_pattern)]
    datacenter: Annotated[str, Meta(min_length=2, max_length=40, pattern=name_pattern)]
    slogan: Annotated[str, Meta(min_length=1, max_length=3000)]
    tag: Annotated[str, Meta(min_length=3, max_length=7)]
    formed: datetime
    member_count: Annotated[int, Meta(ge=1, le=32767)]
    rank: Annotated[int, Meta(ge=1, le=32767)]
    estate_name: Annotated[str, Meta(min_length=1, max_length=100)] | None
    estate_address: Annotated[str, Meta(min_length=1, max_length=100)] | None
    weekly_ranking: Annotated[int, Meta(ge=1, le=32767)] | None
    monthly_ranking: Annotated[int, Meta(ge=1, le=32767)] | None
    greeting: Annotated[str, Meta(min_length=1, max_length=3000)] | None
    active: Annotated[str, Meta(min_length=1, max_length=100)]
    recruiting: bool
