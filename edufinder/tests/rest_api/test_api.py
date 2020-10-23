from django.test import TestCase
from rest_framework.reverse import reverse
from rest_framework.test import APIRequestFactory
from rest_framework.test import force_authenticate
from rest_framework.test import APIClient
from django.contrib.auth.models import User

from edufinder.rest_api.models import Question, Answer, UserAnswer, AnswerChoice


class AnswersApiTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        user = User.objects.create_user(is_superuser=True, username="admin", password="admin")
        self.client.login(username="admin", password="admin")

    def test_POST_question_saved_correct_answer(self):
        question = Question.objects.create(question="What is the answer to life, the universe and everything?")
        userAnswer = UserAnswer.objects.create()

        response = self.client.post(
            f'/question/',
            data={'question': question.pk, 'answer': AnswerChoice.NO, 'userAnswer': userAnswer.pk},
        )

        answer = Answer.objects.first()
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(answer.question, question)
        self.assertEqual(answer.answer, AnswerChoice.NO)
        self.assertEqual(userAnswer, answer.userAnswer)
