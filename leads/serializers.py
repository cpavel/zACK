from rest_framework.serializers import (
    CharField,
    DateTimeField,
    IntegerField,
    Serializer,
)


class SearchTermSerializer(Serializer):
    id = IntegerField(read_only=True)

    term = CharField(max_length=200)

    created_at = DateTimeField(read_only=True)
    updated_at = DateTimeField(read_only=True)
