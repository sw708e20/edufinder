from django.core.management.base import BaseCommand
from edufinder.rest_api.models import AnswerConsensus, Education, Question, AnswerChoice


class Command(BaseCommand):
    help = 'Creates the initial answer consensus'

    def handle(self, *args, **options):
        AnswerConsensus.objects.bulk_create([
            AnswerConsensus(question=question, education=education, answer=AnswerChoice.DONT_KNOW)
            for education in Education.objects.all() for question in Question.objects.all()
        ])
