from django.core.management.base import BaseCommand
from edufinder.rest_api.models import AnswerConsensus, UserAnswer, Answer, AnswerChoice
from edufinder.rest_api.serializers import AnswerChoiceSerializer

class Command(BaseCommand):
    help = 'Updated the answer consensus'

    serializer = AnswerChoiceSerializer()

    def handle(self, *args, **options):
        consensus = {}

        #Iterate over all answers and create a dict for each education and each question under that.
        answers = Answer.objects.all()
        for answer in answers:
            user_answer = answer.userAnswer
            if not consensus.get(user_answer.education.pk):
                consensus[user_answer.education.pk] = {}

            current_education_consensus = consensus[user_answer.education.pk]

            if not current_education_consensus.get(answer.question.pk):
                current_education_consensus[answer.question.pk] = {2:0, 1:0, 0:0, -1:0, -2:0}

            current_question_consensus = current_education_consensus[answer.question.pk]
            int_answer = self.serializer.to_representation(answer.answer)

            current_question_consensus[int_answer] += 1

        updated_answer_consensus = []
        #Iterate over all elements and set what the answer should be.
        for education_key, education_info in consensus.items():
            for question_key, answers in education_info.items():
                int_value = max(answers, key=answers.get)
                consensus_answer = self.serializer.to_internal_value(int_value)

                ac = AnswerConsensus.objects.filter(education__pk=education_key,question__pk=question_key).get()
                ac.answer = consensus_answer
                updated_answer_consensus.append(ac)

        AnswerConsensus.objects.bulk_update(updated_answer_consensus, ['answer'])