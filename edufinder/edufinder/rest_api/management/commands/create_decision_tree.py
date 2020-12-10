from django.core.management.base import BaseCommand
from edufinder.rest_api.management.question_prioritization import create_question_tree
from django.core.cache import cache

class Command(BaseCommand):
    help = 'Creates a decision tree to be used for question prioritization'

    def handle(self, *args, **options):
        timestamp = cache.get('question_tree_timestamp')
        print(f'Previous cache timestamp: {timestamp}')
        create_question_tree()
        