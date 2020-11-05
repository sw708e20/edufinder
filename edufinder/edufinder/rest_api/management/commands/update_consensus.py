from django.core.management.base import BaseCommand
from edufinder.rest_api.models import AnswerConsensus, UserAnswer, Answer, AnswerChoice

class Command(BaseCommand):
    help = 'Updated the answer consensus'

    def handle(self, *args, **options):
        consensus = {}
        conversion_dict = {
            AnswerChoice.YES: 2,
            AnswerChoice.PROBABLY: 1,
            AnswerChoice.DONT_KNOW: 0,
            AnswerChoice.PROBABLY_NOT: -1,
            AnswerChoice.NO: -2,
        }

        #Iterate over all answers and create a dict for each education and each question under that.
        for answer in Answer.objects.all():
            user_answer = answer.userAnswer
            if not consensus.get(user_answer.education.pk):
                consensus[user_answer.education.pk] = {}

            current_education_consensus = consensus[user_answer.education.pk]

            if not current_education_consensus.get(answer.question.pk):
                current_education_consensus[answer.question.pk] = {2:0, 1:0, 0:0, -1:0, -2:0}
            
            current_question_consensus = current_education_consensus[answer.question.pk]

            int_answer = conversion_dict[answer.answer]

            current_question_consensus[int_answer] += 1
        
        print(consensus)
        
        #Iterate over all elements and set what the answer should be.
        for education_key, education_info in consensus.items():
            for question_key, answers in education_info.items():
                education_info[question_key] = max(answers, key=answers.get)

        #Fetch all AnswerConsensus objects and update accordingly to the new data.
        current_answer_consensus = AnswerConsensus.objects.all()

        for answer_consensus in current_answer_consensus:
            answer_consensus.answer = consensus[old_answer_consensus.education.pk][old_answer_consensus.question.pk]

        
        AnswerConsensus.objects.bulk_update(current_answer_consensus, ['answer'])