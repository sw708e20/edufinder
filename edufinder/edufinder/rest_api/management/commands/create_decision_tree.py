from django.core.management.base import BaseCommand
from edufinder.rest_api.management.question_prioritization import CreateQuestionTree

class Command(BaseCommand):
    help = 'Creates a decision tree to be used for question prioritization'

    def handle(self, *args, **options):
        CreateQuestionTree()
        