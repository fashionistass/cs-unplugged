from django.http import QueryDict
from django.test import tag
from tests.BaseTestWithDB import BaseTestWithDB
from resources.generators.JobBadgesResourceGenerator import JobBadgesResourceGenerator


@tag("resource")
class JobBadgesResourceGeneratorTest(BaseTestWithDB):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.language = "en"

    def test_subtitle_a4(self):
        query = QueryDict("paper_size=a4")
        generator = JobBadgesResourceGenerator(query)
        self.assertEqual(
            generator.subtitle,
            "a4"
        )

    def test_subtitle_letter(self):
        query = QueryDict("paper_size=letter")
        generator = JobBadgesResourceGenerator(query)
        self.assertEqual(
            generator.subtitle,
            "letter"
        )
