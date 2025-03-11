from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):

    dependencies = [
        ('parsers', '0001_initial'),  # Make sure this matches your parsers app's migration
        ('inventory', '0002_alter_device_device_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='device',
            name='device_type',
            field=models.ForeignKey(
                help_text='The type/platform of the device',
                on_delete=django.db.models.deletion.CASCADE,
                to='parsers.devicetype',
                verbose_name='Device Type'
            ),
        ),
    ] 