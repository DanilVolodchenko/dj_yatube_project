# Generated by Django 2.2.16 on 2023-03-02 05:44

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('posts', '0009_follow'),
    ]

    operations = [
        migrations.CreateModel(
            name='Appraise',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.AlterModelOptions(
            name='comment',
            options={'verbose_name': 'Комментарий', 'verbose_name_plural': 'Комментарии'},
        ),
        migrations.AddIndex(
            model_name='group',
            index=models.Index(fields=['slug'], name='posts_group_slug_e3a105_idx'),
        ),
        migrations.AddConstraint(
            model_name='follow',
            constraint=models.UniqueConstraint(fields=('user', 'author'), name='unique_follow'),
        ),
        migrations.AddField(
            model_name='appraise',
            name='author',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='appraising', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='appraise',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='appraiser', to=settings.AUTH_USER_MODEL),
        ),
    ]
