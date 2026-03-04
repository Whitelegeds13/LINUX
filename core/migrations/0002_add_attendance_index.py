"""
Migration to add index on attendance_date for better query performance.
"""

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='dailyattendance',
            index=models.Index(fields=['attendance_date'], name='attendance_date_idx'),
        ),
        migrations.AddIndex(
            model_name='tokenreward',
            index=models.Index(fields=['reward_date'], name='reward_date_idx'),
        ),
    ]
