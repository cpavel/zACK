from django.db.models import IntegerChoices as IntEnum


class SearchLocation(IntEnum):
    HACKER_NEWS = 1
    TWITTER = 2


def get_default_search_locations():
    return [SearchLocation.HACKER_NEWS]
