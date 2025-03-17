from enum import StrEnum

__all__ = ["JobRole"]


class JobRole(StrEnum):
    """
    Represents the role of a class or job.

    Attributes:
        TANK (str): Tank job role.
        HEALER (str): Healer job role.
        MELEE_DPS (str): Melee DPS job role.
        PHYSICAL_RANGED_DPS (str): Physical ranged DPS job role.
        MAGICAL_RANGED_DPS (str): Magical ranged DPS job role.
        DISCIPLE_OF_HAND (str): Crafter job role.
        DISCIPLE_OF_LAND (str): Gatherer job role.
        UNKNOWN (str): Unknown job role. This should not be returned unless the library needs to be updated following
            a major expansion.
    """

    TANK = "Tank"
    HEALER = "Healer"
    MELEE_DPS = "Melee DPS"
    PHYSICAL_RANGED_DPS = "Physical Ranged DPS"
    MAGICAL_RANGED_DPS = "Magical Ranged DPS"
    DISCIPLE_OF_HAND = "Disciple of Hand"
    DISCIPLE_OF_LAND = "Disciple of Land"
    UNKNOWN = "Unknown"

    @classmethod
    def from_job_name(cls, job_name: str) -> "JobRole":
        """
        Gets the role of the provided job.

        Args:
            job_name: The name of the job or class

        Returns:
            JobRole: The corresponding job type enum value
        """
        return _JOBS_MAP.get(job_name, cls.UNKNOWN)


# Class-level job mappings (outside the Enum)
_JOBS_MAP = {
    # Tanks
    "Gladiator": JobRole.TANK,
    "Paladin": JobRole.TANK,
    "Marauder": JobRole.TANK,
    "Warrior": JobRole.TANK,
    "Dark Knight": JobRole.TANK,
    "Gunbreaker": JobRole.TANK,
    # Healers
    "Conjurer": JobRole.HEALER,
    "White Mage": JobRole.HEALER,
    "Scholar": JobRole.HEALER,
    "Astrologian": JobRole.HEALER,
    "Sage": JobRole.HEALER,
    # Melee DPS
    "Pugilist": JobRole.MELEE_DPS,
    "Monk": JobRole.MELEE_DPS,
    "Lancer": JobRole.MELEE_DPS,
    "Dragoon": JobRole.MELEE_DPS,
    "Rogue": JobRole.MELEE_DPS,
    "Ninja": JobRole.MELEE_DPS,
    "Samurai": JobRole.MELEE_DPS,
    "Reaper": JobRole.MELEE_DPS,
    "Viper": JobRole.MELEE_DPS,
    # Physical Ranged DPS
    "Archer": JobRole.PHYSICAL_RANGED_DPS,
    "Bard": JobRole.PHYSICAL_RANGED_DPS,
    "Machinist": JobRole.PHYSICAL_RANGED_DPS,
    "Dancer": JobRole.PHYSICAL_RANGED_DPS,
    # Magical Ranged DPS
    "Thaumaturge": JobRole.MAGICAL_RANGED_DPS,
    "Black Mage": JobRole.MAGICAL_RANGED_DPS,
    "Arcanist": JobRole.MAGICAL_RANGED_DPS,
    "Summoner": JobRole.MAGICAL_RANGED_DPS,
    "Red Mage": JobRole.MAGICAL_RANGED_DPS,
    "Pictomancer": JobRole.MAGICAL_RANGED_DPS,
    "Blue Mage (Limited Job)": JobRole.MAGICAL_RANGED_DPS,
    # Disciples of Hand (Crafters)
    "Weaver": JobRole.DISCIPLE_OF_HAND,
    "Carpenter": JobRole.DISCIPLE_OF_HAND,
    "Blacksmith": JobRole.DISCIPLE_OF_HAND,
    "Armorer": JobRole.DISCIPLE_OF_HAND,
    "Goldsmith": JobRole.DISCIPLE_OF_HAND,
    "Leatherworker": JobRole.DISCIPLE_OF_HAND,
    "Alchemist": JobRole.DISCIPLE_OF_HAND,
    "Culinarian": JobRole.DISCIPLE_OF_HAND,
    # Disciples of Land (Gatherers)
    "Botanist": JobRole.DISCIPLE_OF_LAND,
    "Miner": JobRole.DISCIPLE_OF_LAND,
    "Fisher": JobRole.DISCIPLE_OF_LAND,
}
