#
#

import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ack.settings")
django.setup()

from ack.tasks import search_leads, async_search_term_by_id
from ack import enums
from django.contrib.auth.models import User

me = User.objects.get(username="admin")  # Search for this user.
# result = search_leads(enums.SearchLocation.HACKER_NEWS, user_id=me.id)  # Get sync result.
result = async_search_term_by_id(search_term_id=1)  # Get sync result.
