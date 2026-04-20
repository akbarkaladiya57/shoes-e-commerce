from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("product_app", "0003_rating_avgrate"),
    ]

    operations = [
        migrations.AlterField(
            model_name="productimage",
            name="image",
            field=models.ImageField(upload_to="products/"),
        ),
    ]
