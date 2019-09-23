from django.db import migrations, models
import uuid

def create_uuid(apps, schema_editor):
    User = apps.get_model('users', 'User')
    for user in User.objects.all():
        user.uuid = uuid.uuid4()
        user.save()

class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='uuid',
            field=models.UUIDField(blank=True, null=True),
        ),
        migrations.RunPython(create_uuid),
        migrations.AlterField(
            model_name='user',
            name='uuid',
            field=models.UUIDField(unique=True, editable=False)
        )
    ]
