from django.db import migrations, models


def populate_course_codes(apps, schema_editor):
    Course = apps.get_model("courses", "Course")
    for course in Course.objects.order_by("pk").iterator():
        course.code = f"CRS{course.pk:05d}"
        course.save(update_fields=["code"])


class Migration(migrations.Migration):
    dependencies = [
        ("courses", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="course",
            name="code",
            field=models.CharField(max_length=30, null=True, unique=True),
        ),
        migrations.RunPython(populate_course_codes, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="course",
            name="code",
            field=models.CharField(blank=True, max_length=30, unique=True),
        ),
    ]
