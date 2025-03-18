Overview
============

xivlodestone is a Python library that interacts with the
`Lodestone <https://na.finalfantasyxiv.com/lodestone/>`__ website.

Its primary focus is to provide developers with a simple, easy-to-use
interface for retrieving up-to-date character information.

It currently supports searching for and retrieving character and free
company details. Additional features may be added in the future.

As this project is currently in alpha testing, it is not guaranteed to
be stable or feature-complete. Breaking changes may occur anytime, and
the API may change without notice.

Installation
============

You can install this library using pip:

.. code:: shell

   pip install xivlodestone

Usage
=====

You can use the ``search_character`` method to search for a character.
With a correctly spelled character name and world, this is usually a
single character.

Otherwise, you will get a list of characters that match the search
criteria.

.. code:: python

   import asyncio
   from xivlodestone import LodestoneScraper

   async def search_example():
       lodestone = LodestoneScraper()
       async for character in lodestone.search_characters("Yoshi'p Sampo", "Mandragora"):
           print(f"Found {character.name} from {character.world}")

       # Or if you need to pre-populate the results into a list
       characters = [c async for c in lodestone.search_characters("Yoshi'p Sampo", "Mandragora")]

   asyncio.run(search_example())

By default, the library will only fetch a maximum of 50 (the first page
of) results.

You can set the ``limit`` parameter to a higher value to fetch more
results or None to fetch the maximum number of results (up to 1,000).

Search results will only provide basic information about a character,
such as their name, world, and avatar.

You can use the ``get_character`` method to fetch more details about the
character.

.. code:: python

   from xivlodestone import LodestoneScraper

   async def get_character_example():
       lodestone = LodestoneScraper()
       characters = [c async for c in lodestone.search_characters("Yoshi'p Sampo", "Mandragora")]
       character = await lodestone.get_character(characters[0])  # Also accepts a character ID
       print(f"{character.name} from {character.world}")
       print(f"Nameday: {character.nameday}")
       print(f"Bio: {character.bio}")
       if character.free_company:
           print(f"Free Company: {character.free_company.name}")

A common use case for scraping a character’s lodestone profile page is
verifying a user’s ownership.

This is often done by asking the user to insert a temporary verification
code into their character’s bio section and then scraping their profile
page to verify it.

With xivlodestone, this can be done with just a few lines of code:

.. code:: python

   from xivlodestone import LodestoneScraper

   async def verify_character_bio(character_id: int, verification_code: str):
       lodestone = LodestoneScraper()
       character = await lodestone.get_character(character_id)
       if verification_code in character.bio:


Links
=====
- `Documentation <https://xivlodestone.readthedocs.io/en/latest/index.html>`__