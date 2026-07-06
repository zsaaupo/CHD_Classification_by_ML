from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('predictor', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='predictionresult',
            name='risk_level',
        ),
    ]
