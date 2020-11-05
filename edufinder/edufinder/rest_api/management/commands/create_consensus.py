from django.core.management.base import BaseCommand
from edufinder.rest_api.models import AnswerConsensus, Education, Question, AnswerChoice

class Command(BaseCommand):
    help = 'Creates the initial answer consensus'

    def handle(self, *args, **options):
        educations = Education.objects.all()
        questions = Question.objects.all()
        acs = []
        for education in educations:
            for question in questions:
                ac = AnswerConsensus(question=question, education=education, answer=AnswerChoice.DONT_KNOW)
                acs.append(ac)

        AnswerConsensus.objects.bulk_create(acs)