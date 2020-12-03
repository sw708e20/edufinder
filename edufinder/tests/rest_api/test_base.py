from django.test import TestCase
from edufinder.rest_api.models import Question, Answer, UserAnswer, AnswerChoice, Education, EducationType

class TestBase(TestCase):
    def create_questions(self):
        questions = [Question(en=f'question #{i}?', da=f'question #{i}?') for i in range(30)]
        Question.objects.bulk_create(questions)

    def create_educations(self):
        educations = [Education(name = f'Education #{i}', description="description") for i in range(10)]
        Education.objects.bulk_create(educations)

        educations = Education.objects.all()
        education_types = [EducationType(education=educations[i], name=f'EducationType #{i}', url="http://example.com") for i in range(len(educations))]
        EducationType.objects.bulk_create(education_types)

    def get_answered_questions(self):
        self.create_questions()
        self.create_educations()
        questions = Question.objects.all()
        yes_value = AnswerChoice.YES
        return [{"id": questions[i].pk, "answer": yes_value} for i in range(20)]