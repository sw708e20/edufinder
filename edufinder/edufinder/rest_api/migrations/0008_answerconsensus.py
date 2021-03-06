from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('rest_api', '0007_question_lang_fields'),
    ]

    operations = [
        migrations.CreateModel(
            name='AnswerConsensus',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('answer', models.CharField(choices=[('Yes', 'Yes'), ('No', 'No'), ('Probably', 'Probably'), ('Probably not', 'Probably Not'), ("Don't know", 'Dont Know')], max_length=20)),
                ('education', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='rest_api.education')),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='rest_api.question')),
            ],
            options={
                'unique_together': {('education', 'question')},
            },
        ),
    ]
