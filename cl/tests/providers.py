import random

from faker import Faker
from faker.providers import BaseProvider
from juriscraper.lib.string_utils import titlecase

from cl.custom_filters.templatetags.text_filters import oxford_join

fake = Faker()


class LegalProvider(BaseProvider):
    def random_id(self) -> str:
        """Generate a random ID that can be used in a handful of places like:

         - The PK of the court (because they use chars)
         - the cl_id field of people

        :return a str with random chars
        """
        return "".join(fake.random_letters(length=15)).lower()

    def court_name(self) -> str:
        """
        Generate court names like:

         - First circuit for the zoo
         - District court of albatross
         - Appeals court of eczema

        :return: A court name
        """
        first_word = random.choice(
            [
                "Thirteenth circuit",
                "District court",
                "Appeals court",
                "Superior court",
            ]
        )
        mid_word = random.choice(["of the", "for the"])
        last_word = random.choice(
            [
                "Zoo",
                "Medical Worries",
                "Programming Horrors",
                "dragons",
                "Dirty Dishes",
                "Eruptanyom",  # Kelvin's pretend world
            ]
        )

        return " ".join([first_word, mid_word, last_word])

    def federal_district_docket_number(self) -> str:
        """Make a docket number like you'd see in a district court, of the
        form, "2:13-cv-03239"
        """
        office = random.randint(1, 7)
        year = random.randint(0, 99)
        letters = random.choice(["cv", "bk", "cr", "ms"])
        number = random.randint(1, 200_000)
        return f"{office}:{year:02}-{letters}-{number:05}"

    @staticmethod
    def _make_random_party(full: bool = False) -> str:
        do_company = random.choice([True, False])
        if do_company:
            if full:
                return oxford_join([fake.company() for _ in range(5)])
            else:
                return fake.company()
        else:
            if full:
                return oxford_join([fake.name() for _ in range(5)])
            else:
                return fake.last_name()

    def case_name(self, full: bool = False) -> str:
        """Makes a clean case name like "O'Neil v. Jordan" """
        plaintiff = self._make_random_party(full)
        defendant = self._make_random_party(full)
        return titlecase(f"{plaintiff} v. {defendant}")
