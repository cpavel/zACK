from rest_framework import routers

from .views import SearchTermListView

router = routers.SimpleRouter()

router.register("search_term", SearchTermListView)

urlpatterns = router.urls
