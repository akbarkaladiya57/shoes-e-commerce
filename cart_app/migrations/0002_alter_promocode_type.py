from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("cart_app", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="promocode",
            name="type",
            field=models.CharField(
                choices=[("flat", "flat"), ("percentage", "percentage")], max_length=50
            ),
        ),
    ]
