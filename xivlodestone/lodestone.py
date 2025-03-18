import re
import urllib.parse
from datetime import datetime
from typing import Optional, Literal, AsyncGenerator

from bs4 import BeautifulSoup
from msgspec import convert

from xivlodestone.enums import JobRole
from xivlodestone.errors import LodestoneError
from xivlodestone.models import (
    SimpleCharacter,
    Character,
    CharacterGrandCompany,
    SimpleFreeCompany,
    CharacterJob,
    FreeCompany,
    CharacterMinion,
    CharacterMount,
    CharacterFacewear,
    CharacterStats,
)
from xivlodestone.scraper import BaseScraper

__all__ = ["LodestoneScraper"]


class LodestoneScraper(BaseScraper):
    """Async client for scraping character data from FFXIV Lodestone."""

    BASE_URL = "https://na.finalfantasyxiv.com"
    LODESTONE_URL = f"{BASE_URL}/lodestone"
    CHARACTER_URL = f"{LODESTONE_URL}/character"
    FREE_COMPANY_URL = f"{LODESTONE_URL}/freecompany"

    async def search_characters(
        self, name: str, world: Optional[str] = None, *, limit: int | None = 50
    ) -> AsyncGenerator[SimpleCharacter, None]:
        """
        Searches for a character by name and optionally world.

        The returned SimpleCharacter models can be passed to the `get_character` method if you need
        more detailed character information.

        Args:
            name: Character name to search for.
            world: Optional world/server name to filter by.
            limit: Optional limit on the number of results to return. Defaults to 50 (one page of results).

        Returns:
            AsyncGenerator[SimpleCharacter, None]: An async generator yielding SimpleCharacter models.
        """
        # Request
        params = {
            "q": name.replace(" ", "+"),
        }
        if world:
            params["worldname"] = world.title()
        url = f"{self.CHARACTER_URL}/?{urllib.parse.urlencode(params)}"
        next_page = url

        index = 0
        while next_page:
            soup = BeautifulSoup(await self._fetch_page(next_page), "html.parser")
            # Make sure we have results
            if soup.select_one(".parts__zero:-soup-contains('Your search yielded no results')"):
                return

            next_page = self._get_attr(soup.select_one(".btn__pager .btn__pager__next"), "href")
            if not next_page.startswith(self.CHARACTER_URL):
                next_page = None

            character_elements = soup.select(".ldst__main .entry")
            for elem in character_elements:
                # Grab character elements
                char_link = elem.select_one("a.entry__link")
                name_elem = elem.select_one(".entry__name")
                world_elem = elem.select_one(".entry__world")
                avatar_elem = elem.select_one(".entry__chara__face img")

                # Extract character values
                char_url: str = self._get_attr(char_link, "href")
                char_name: str = self._get_text(name_elem)
                char_first_name, char_last_name = char_name.split(" ", 1)
                char_world, char_datacenter = self._split_server_string(world_elem.text)
                char_avatar: str = self._get_attr(avatar_elem, "src")

                # Add to results
                yield convert(
                    {
                        "id": self.id_from_character_url(f"{self.BASE_URL}{char_url}"),
                        "lodestone_url": f"{self.BASE_URL}{char_url}",
                        "first_name": char_first_name,
                        "last_name": char_last_name,
                        "world": char_world,
                        "datacenter": char_datacenter,
                        "avatar_url": char_avatar,
                    },
                    SimpleCharacter,
                )

                index += 1
                if limit and index >= limit:
                    next_page = None
                    break

    async def get_character(self, character: SimpleCharacter | int) -> Character:
        """
        Retrieves detailed information about a character.

        Args:
            character: The character's Lodestone ID or a SimpleCharacter model.

        Returns:
            Character model containing detailed information about the character.
        """
        character_id = character.id if isinstance(character, SimpleCharacter) else character
        url = f"{self.CHARACTER_URL}/{character_id}/"
        soup = BeautifulSoup(await self._fetch_page(url), "html.parser")

        character_elem = soup.select_one("#character")

        # Grab character elements
        name_elem = character_elem.select_one(".frame__chara__name")
        title_elem = character_elem.select_one(".frame__chara__title")
        avatar_elem = character_elem.select_one(".frame__chara__face img")
        portrait_elem = character_elem.select_one(".character__detail__image img")
        bio_elem = character_elem.select_one(".character__selfintroduction")
        world_elem = character_elem.select_one(".frame__chara__world")
        race_elem = character_elem.select_one(
            '.character-block__box:has(.character-block__title:-soup-contains("Race/Clan/Gender")) .character-block__name'
        )
        nameday_elem = character_elem.select_one(".character-block__birth")
        guardian_elem = character_elem.select_one(
            '.character-block__box:has(.character-block__title:-soup-contains("Guardian")) .character-block__name'
        )
        city_state_elem = character_elem.select_one(
            '.character-block__box:has(.character-block__title:-soup-contains("City-state")) .character-block__name'
        )
        gc_elem = character_elem.select_one(
            '.character-block__box:has(.character-block__title:-soup-contains("Grand Company")) .character-block__name'
        )
        fc_elem = character_elem.select_one(".character__freecompany__name a")
        fc_crest_elem = character_elem.select(".character__freecompany__crest__image img")
        level_elem = character_elem.select_one(".character__class__data")

        # Extract character values
        char_name: str = self._get_text(name_elem)
        char_first_name, char_last_name = char_name.split(" ", 1)
        char_title: str | None = self._get_text(title_elem) if title_elem else None
        char_avatar: str = self._get_attr(avatar_elem, "src")
        char_portrait: str = self._get_attr(portrait_elem, "src")
        char_bio: str = self._get_text(bio_elem)
        char_bio: str = (
            "" if char_bio == "-" else char_bio
        )  # "-" is the Lodestone's default placeholder for empty bios
        char_world, char_datacenter = self._split_server_string(world_elem.text)
        char_race, _clan_gender = race_elem.decode_contents().strip().split("<br/>")
        char_clan, char_gender = _clan_gender.strip().split(" / ")
        char_gender: Literal["male", "female"] = "male" if char_gender == "♂" else "female"
        char_nameday: str = self._get_text(nameday_elem)
        char_guardian: str = self._get_text(guardian_elem)
        char_city_state: str | None = self._get_text(city_state_elem) if city_state_elem else None
        _char_gc_split: tuple[str] | None = (
            self._get_text(gc_elem).split(" / ") if gc_elem else None
        )
        char_gc: CharacterGrandCompany = (
            convert({"name": _char_gc_split[0], "rank": _char_gc_split[1]}, CharacterGrandCompany)
            if _char_gc_split
            else None
        )
        char_fc_link: str | None = self._get_attr(fc_elem, "href") if fc_elem else None
        char_fc: SimpleFreeCompany = (
            convert(
                {
                    "id": self.id_from_free_company_url(char_fc_link),
                    "lodestone_url": f"{self.BASE_URL}{char_fc_link}",
                    "name": self._get_text(fc_elem),
                    "crest_component_urls": [self._get_attr(e, "src") for e in fc_crest_elem],
                },
                SimpleFreeCompany,
            )
            if fc_elem
            else None
        )
        char_level: int = int(self._get_text(level_elem).replace("LEVEL ", ""))

        jobs = self._parse_character_jobs(soup)
        return convert(
            {
                "id": character_id,
                "lodestone_url": url,
                "first_name": char_first_name,
                "last_name": char_last_name,
                "world": char_world,
                "datacenter": char_datacenter,
                "avatar_url": char_avatar,
                "portrait_url": char_portrait,
                "title": char_title,
                "bio": char_bio,
                "gender": char_gender,
                "race": char_race,
                "clan": char_clan,
                "nameday": char_nameday,
                "guardian": char_guardian,
                "city_state": char_city_state,
                "grand_company": char_gc,
                "free_company": char_fc,
                "level": char_level,
                "jobs": jobs,
                "current_job": self._parse_current_job(soup, jobs),
                "stats": self._parse_character_stats(soup),
            },
            Character,
        )

    async def character_minions(self, character: SimpleCharacter | int) -> list[CharacterMinion]:
        """
        Retrieves a list of minions owned by a character.

        Args:
            character: The character's Lodestone ID or a SimpleCharacter model.

        Returns:
            list[CharacterMinion]: A list of CharacterMinion models representing the character's minions.
        """
        character_id = character.id if isinstance(character, SimpleCharacter) else character
        url = f"{self.CHARACTER_URL}/{character_id}/minion/"
        soup = BeautifulSoup(await self._fetch_page(url, mobile=True), "html.parser")

        # Grab minion elements
        minions = []
        minion_elements = soup.select("li.minion__list__item")
        for elem in minion_elements:
            img_elem = elem.select_one("img.minion__list__icon__image")
            name_elem = elem.select_one("span.minion__name")
            minions.append(
                convert(
                    {
                        "name": self._get_text(name_elem),
                        "icon_url": self._get_attr(img_elem, "src"),
                    },
                    CharacterMinion,
                )
            )

        return minions

    async def character_mounts(self, character: SimpleCharacter | int) -> list[CharacterMount]:
        """
        Retrieves a list of mounts owned by a character.

        Args:
            character: The character's Lodestone ID or a SimpleCharacter model.

        Returns:
            list[CharacterMount]: A list of CharacterMount models representing the character's mounts.
        """
        character_id = character.id if isinstance(character, SimpleCharacter) else character
        url = f"{self.CHARACTER_URL}/{character_id}/mount/"
        soup = BeautifulSoup(await self._fetch_page(url, mobile=True), "html.parser")

        # Grab minion elements
        mounts = []
        mount_elements = soup.select("li.mount__list__item")
        for elem in mount_elements:
            img_elem = elem.select_one("img.mount__list__icon__image")
            name_elem = elem.select_one("span.mount__name")
            mounts.append(
                convert(
                    {
                        "name": self._get_text(name_elem),
                        "icon_url": self._get_attr(img_elem, "src"),
                    },
                    CharacterMount,
                )
            )

        return mounts

    async def character_facewear(
        self, character: SimpleCharacter | int
    ) -> list[CharacterFacewear]:
        """
        Retrieves a list of facewear items owned by a character.

        Args:
            character: The character's Lodestone ID or a SimpleCharacter model.

        Returns:
            list[CharacterFacewear]: A list of CharacterFacewear models representing the character's facewear items.
        """
        character_id = character.id if isinstance(character, SimpleCharacter) else character
        url = f"{self.CHARACTER_URL}/{character_id}/faceaccessory/"
        soup = BeautifulSoup(await self._fetch_page(url, mobile=True), "html.parser")

        # Grab minion elements
        facewear = []
        facewear_elements = soup.select("li.faceaccessory__list__item")
        for elem in facewear_elements:
            img_elem = elem.select_one("img.faceaccessory__list__icon__image")
            name_elem = elem.select_one("span.faceaccessory__name")
            facewear.append(
                convert(
                    {
                        "name": self._get_text(name_elem),
                        "icon_url": self._get_attr(img_elem, "src"),
                    },
                    CharacterFacewear,
                )
            )

        return facewear

    async def get_free_company(self, free_company: SimpleFreeCompany | int) -> FreeCompany:
        """
        Retrieves detailed information about a free company.

        Args:
            free_company: The free company's Lodestone ID or a SimpleFreeCompany model.

        Returns:
            FreeCompany model containing detailed information about the free company.
        """
        free_company_id = (
            free_company.id if isinstance(free_company, SimpleFreeCompany) else free_company
        )
        url = f"{self.FREE_COMPANY_URL}/{free_company_id}/"
        soup = BeautifulSoup(await self._fetch_page(url), "html.parser")

        # Grab FC elements
        grand_company_elem = soup.select_one(".entry__freecompany__gc")
        name_elem = soup.select_one(".entry__freecompany__name")
        world_elem = soup.select_one(".entry__freecompany__gc > .xiv-lds-home-world").parent
        slogan_elem = soup.select_one(".freecompany__text__message")
        tag_elem = soup.select_one(".freecompany__text.freecompany__text__tag")
        formed_elem = soup.select_one(
            ".heading--lead:-soup-contains('Formed') + p.freecompany__text script"
        )
        member_count_elem = soup.select_one(
            ".heading--lead:-soup-contains('Active Members') + p.freecompany__text"
        )
        rank_elem = soup.select_one(".heading--lead:-soup-contains('Rank') + p.freecompany__text")
        estate_name_elem = soup.select_one("p.freecompany__estate__name")
        estate_address_elem = soup.select_one("p.freecompany__estate__text")
        greeting_elem = soup.select_one("p.freecompany__estate__greeting")
        active_elem = soup.select(".heading--lead:-soup-contains('Active') + p.freecompany__text")[
            1
        ]
        recruitment_status_elem = soup.select_one(
            ".heading--lead:-soup-contains('Recruitment') + p.freecompany__text"
        )
        fc_crest_elem = soup.select(
            ".character__freecompany__crest__image img, .entry__freecompany__crest__image img"
        )
        # todo: focus, seeking?

        # Extract FC values
        fc_grand_company: str = grand_company_elem.text.split("<")[
            0
        ].strip()  # stripping the "<Allied>" tidbit out
        fc_name: str = self._get_text(name_elem)
        fc_world, fc_datacenter = self._split_server_string(world_elem.text)
        fc_slogan: str = self._get_text(slogan_elem)
        fc_tag: str = tag_elem.text.strip(" «»")
        _fc_formed_re = re.search(
            r"ldst_strftime\((?P<timestamp>\d{10}), 'YMD'\)", formed_elem.text
        )
        fc_formed: int = int(_fc_formed_re.group("timestamp"))
        fc_member_count: int = int(self._get_text(member_count_elem))
        fc_rank: int = int(self._get_text(rank_elem))
        fc_estate_name: str = self._get_text(estate_name_elem) if estate_name_elem else None
        fc_estate_address: str = (
            self._get_text(estate_address_elem) if estate_address_elem else None
        )
        fc_weekly_ranking, fc_monthly_ranking = self._parse_free_company_rankings(soup)
        fc_greeting: str = self._get_text(greeting_elem) if greeting_elem else None
        fc_active: str = self._get_text(active_elem)
        fc_recruitment_status: str = self._get_text(recruitment_status_elem)

        return convert(
            {
                "id": free_company_id,
                "lodestone_url": url,
                "grand_company": fc_grand_company,
                "name": fc_name,
                "world": fc_world,
                "datacenter": fc_datacenter,
                "slogan": fc_slogan,
                "tag": fc_tag,
                "formed": datetime.fromtimestamp(fc_formed),
                "member_count": fc_member_count,
                "rank": fc_rank,
                "estate_name": fc_estate_name,
                "estate_address": fc_estate_address,
                "weekly_ranking": fc_weekly_ranking,
                "monthly_ranking": fc_monthly_ranking,
                "greeting": fc_greeting,
                "active": fc_active,
                "recruiting": fc_recruitment_status.lower() == "open",
                "crest_component_urls": [self._get_attr(e, "src") for e in fc_crest_elem],
            },
            FreeCompany,
        )

    async def free_company_members(
        self, free_company: SimpleFreeCompany | int, *, limit: int | None = None
    ) -> AsyncGenerator[SimpleCharacter, None]:
        """
        Retrieves a list of players in a free company.

        The returned SimpleCharacter models can be passed to the `get_character` method if you need
        more detailed character information.

        Args:
            free_company: The free company's Lodestone ID or a SimpleFreeCompany model.
            limit: Optional limit on the number of results to return. Defaults to None (no limit).

        Returns:
            AsyncGenerator[SimpleCharacter, None]: An async generator yielding SimpleCharacter models.
        """
        fc_id = free_company.id if isinstance(free_company, FreeCompany) else free_company
        url = f"{self.FREE_COMPANY_URL}/{fc_id}/member/"
        next_page = url

        index = 0
        while next_page:
            soup = BeautifulSoup(await self._fetch_page(next_page), "html.parser")
            next_page = self._get_attr(soup.select_one(".btn__pager .btn__pager__next"), "href")
            if not next_page.startswith(url):
                next_page = None

            member_elements = soup.select(".ldst__window ul li.entry")
            for elem in member_elements:
                # Grab member elements
                link_elem = elem.select_one("a.entry__bg")
                avatar_elem = elem.select_one(".entry__chara__face > img")
                name_elem = elem.select_one(".entry__freecompany__center > .entry__name")
                world_elem = elem.select_one(".entry__freecompany__center > .entry__world")

                # Extract member values
                member_url: str = f"{self.BASE_URL}{self._get_attr(link_elem, 'href')}"
                member_avatar: str = self._get_attr(avatar_elem, "src")
                member_first_name, member_last_name = self._get_text(name_elem).split(" ", 1)
                member_world, member_datacenter = self._split_server_string(world_elem.text)

                yield convert(
                    {
                        "id": fc_id,
                        "lodestone_url": member_url,
                        "first_name": member_first_name,
                        "last_name": member_last_name,
                        "world": member_world,
                        "datacenter": member_datacenter,
                        "avatar_url": member_avatar,
                    },
                    SimpleCharacter,
                )

                index += 1
                if limit and index >= limit:
                    next_page = None
                    break

    @classmethod
    def id_from_character_url(cls, url: str) -> int:
        """
        Extracts the character ID from a Lodestone URL.

        Args:
            url: Character's Lodestone URL.

        Returns:
            int: The character ID.
        """
        char_id_match = re.match(
            rf"({re.escape(cls.BASE_URL)})?/lodestone/character/(?P<char_id>\d{{1,38}})/", url
        )
        if not char_id_match:
            raise LodestoneError("Character URL is in an unrecognized format", url)
        return int(char_id_match.group("char_id"))

    @classmethod
    def id_from_free_company_url(cls, url: str) -> int:
        """
        Extracts the free company ID from a Lodestone URL.

        Args:
            url: Free company's Lodestone URL.

        Returns:
            int: The free company ID.
        """
        fc_id_match = re.match(
            rf"({re.escape(cls.BASE_URL)})?/lodestone/freecompany/(?P<fc_id>\d{{1,38}})/", url
        )
        if not fc_id_match:
            raise LodestoneError("Free company URL is in an unrecognized format", url)
        return int(fc_id_match.group("fc_id"))

    def _parse_character_jobs(self, soup: BeautifulSoup) -> list[CharacterJob]:
        """
        Parses character jobs from the soup object.

        Args:
            soup: BeautifulSoup object containing the character page's HTML.

        Returns:
            List of CharacterJob models.
        """
        job_elements = soup.select(
            ".character__profile__detail > .js__character_toggle:not(.hide) li"
        )
        jobs = []

        for elem in job_elements:
            img_elem = elem.select_one("img")

            name: str = img_elem.get("data-tooltip").split(" / ")[0].strip()
            _level_text = self._get_text(elem)
            level: int = 0 if _level_text == "-" else int(_level_text)
            icon: str = self._get_attr(img_elem, "src")

            jobs.append(
                convert(
                    {
                        "name": name,
                        "level": level,
                        "icon_url": icon,
                        "role": JobRole.from_job_name(name),
                    },
                    CharacterJob,
                )
            )

        return jobs

    def _parse_current_job(self, soup: BeautifulSoup, jobs: list[CharacterJob]) -> CharacterJob | None:
        """
        Figures out what our current job is by cross-referencing icon URL's on the page.
        Args:
            soup(BeautifulSoup): BeautifulSoup object containing the character page's HTML.
            jobs(list[CharacterJob]): List of jobs to check against.

        Returns:
            CharacterJob | None: The currently active class or job on the character. This should virtually never
                return None, but I can imagine a fringe case scenario where someone logs out with no job stone
                equipped even though their job is unlocked. Theoretically, this could cause them to have an icon
                for the class, not the job listed. It could be possible to address this later, but it's such a niche
                case that it's not worth it for now.
        """
        current_job_icon_url = self._get_attr(soup.select_one(".character__class_icon > img"), "src")
        for job in jobs:
            if job.icon_url == current_job_icon_url:
                return job

    def _parse_character_stats(self, soup: BeautifulSoup) -> CharacterStats:
        """
        Parses character stats from the soup object.

        Args:
            soup: BeautifulSoup object containing the character page's HTML.

        Returns:
            CharacterStats model containing the parsed stats.
        """
        stats_elem = soup.select_one(".js__character_toggle.hide")

        stats = {
            "strength": None,
            "dexterity": None,
            "vitality": None,
            "intelligence": None,
            "mind": None,
            "critical_hit_rate": None,
            "determination": None,
            "direct_hit_rate": None,
            "defense": None,
            "magic_defense": None,
            "attack_power": None,
            "skill_speed": None,
            "attack_magic_potency": None,
            "healing_magic_potency": None,
            "spell_speed": None,
            "tenacity": None,
            "piety": None,
            "craftsmanship": None,
            "control": None,
            "gathering": None,
            "perception": None,
            "hp": self._get_text(soup.select_one("p.character__param__text__hp--en-us + span")),
            "mp": self._get_text_or_none(
                soup.select_one("p.character__param__text__mp--en-us + span")
            ),
            "gp": self._get_text_or_none(
                soup.select_one("p.character__param__text__gp--en-us + span")
            ),
            "cp": self._get_text_or_none(
                soup.select_one("p.character__param__text__cp--en-us + span")
            ),
        }

        for elem in stats_elem.select("tr"):
            stat_name = self._get_text(elem.select_one("th span"))
            stat_value = self._get_text(elem.select_one("td"))

            key = stat_name.lower().replace(" ", "_")
            if key not in stats:
                continue

            stats[key] = stat_value

        stats["job_type"] = "combat" if stats["mp"] else "gathering" if stats["gp"] else "crafting"

        return convert(stats, CharacterStats, strict=False)

    # noinspection PyMethodMayBeStatic
    def _parse_free_company_rankings(self, soup: BeautifulSoup) -> tuple[int | None, int | None]:
        """
        Parses free company rankings from the soup object.

        Args:
            soup: BeautifulSoup object containing the free company page's HTML.

        Returns:
            Tuple of weekly and monthly rankings.
        """
        weekly_ranking_elem = soup.select_one("table.character__ranking__data tr:nth-child(1) th")
        monthly_ranking_elem = soup.select_one("table.character__ranking__data tr:nth-child(2) th")

        weekly_ranking_value = None
        if weekly_ranking_elem:
            weekly_match = re.search(r"Weekly Rank:(\d{1,3})", weekly_ranking_elem.text)
            if weekly_match:
                weekly_ranking_value = int(weekly_match.group(1))

        monthly_ranking_value = None
        if monthly_ranking_elem:
            monthly_match = re.search(r"Monthly Rank:(\d{1,3})", monthly_ranking_elem.text)
            if monthly_match:
                monthly_ranking_value = int(monthly_match.group(1))

        return weekly_ranking_value, monthly_ranking_value

    # noinspection PyMethodMayBeStatic
    def _split_server_string(self, server: str) -> tuple[str, str]:
        """
        Splits a server string into world and datacenter components.

        Args:
            server: The server string to split.

        Returns:
            Tuple containing the world name and datacenter.
        """
        world, datacenter = server.strip().rstrip("]").split(" [")
        return world, datacenter
