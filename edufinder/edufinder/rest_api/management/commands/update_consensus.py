from django.core.management.base import BaseCommand
from edufinder.rest_api.models import AnswerConsensus, UserAnswer, Answer, AnswerChoice
from edufinder.rest_api.models import Education, Question
from rest_framework import serializers


class Command(BaseCommand):
    help = 'Updated the answer consensus'

    serializer = serializers.ChoiceField(required=True, choices=AnswerChoice)

    def handle(self, *args, **options):
        self.ensure_consensus_exists()
        consensus = self._create_consensus_dict()
        updated_answer_consensus = []

        # Iterate over all elements and set what the answer should be.
        for education_key, education_info in consensus.items():
            for question_key, answers in education_info.items():

                ac = AnswerConsensus.objects.filter(education__pk=education_key,
                                                    question__pk=question_key).get()
                ac.answer = self.serializer.to_internal_value(max(answers, key=answers.get))
                updated_answer_consensus.append(ac)

        AnswerConsensus.objects.bulk_update(updated_answer_consensus, ['answer'])

    def _create_consensus_dict(self) -> dict:
        consensus = {}
        # Iterate over all answers and create a dict for each education and each question under that
        for answer in Answer.objects.all():
            edu_pk, q_pk = answer.userAnswer.education.pk, answer.question.pk

            if not consensus.get(edu_pk):
                consensus[edu_pk] = {}

            if not consensus[edu_pk].get(q_pk):
                consensus[edu_pk][q_pk] = {2: 0, 1: 0, 0: 0, -1: 0, -2: 0}

            consensus[edu_pk][q_pk][self.serializer.to_representation(answer.answer)] += 1
        return consensus

    @staticmethod
    def ensure_consensus_exists():
        AnswerConsensus.objects.bulk_create([
            AnswerConsensus(question=question, education=education, answer=AnswerChoice.DONT_KNOW)
            for education in Education.objects.all()
            for question in Question.objects.all()
            if not AnswerConsensus.objects.filter(education=education, question=question).exists()])
