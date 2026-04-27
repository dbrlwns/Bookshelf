from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("blogs", "0004_remove_comment_parent"),
    ]

    operations = [
        migrations.CreateModel(
            name="Tag",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=50, unique=True)),
                ("slug", models.SlugField(blank=True, max_length=60, unique=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "ordering": ["name"],
            },
        ),
        migrations.AddField(
            model_name="blog",
            name="tags",
            field=models.ManyToManyField(blank=True, related_name="blogs", to="blogs.tag"),
        ),
    ]
