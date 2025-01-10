from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("data", "0002_searchterm_location_searchterm_user"),
    ]

    operations = [migrations.RenameModel("Template", "PromptTemplate")]
