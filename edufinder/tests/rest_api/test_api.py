from django.test import TestCase
from rest_framework.reverse import reverse
from rest_framework.test import APIRequestFactory
from rest_framework.test import force_authenticate
from rest_framework.test import APIClient
from django.contrib.auth.models import User
import json

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

    def test_POST_answer_saved(self):
        from datetime import datetime, timezone, timedelta
        ip_addr = "127.0.0.1"
        question1 = Question.objects.create(question="Test question")
        question2 = Question.objects.create(question="Test question")
        response = self.client.post('/recommend/',
            data=json.dumps([
                {"id": question1.pk, "answer": 2}, 
                {"id": question2.pk, "answer": -2}]),
            content_type="application/json",
            REMOTE_ADDR=ip_addr,
        )
        
        ua = UserAnswer.objects.first()

        self.assertIsNotNone(ua)
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(ua.datetime)
        self.assertTrue(abs(ua.datetime - datetime.now(timezone.utc)) < timedelta(seconds=1))
        self.assertIsNotNone(ua.ip_addr)
        self.assertEqual(ua.ip_addr, ip_addr)
        answer1 = Answer.objects.get(userAnswer=ua, question=question1)
        self.assertIsNotNone(answer1)
        self.assertIsNotNone(answer1.userAnswer)
        answer2 = Answer.objects.get(userAnswer=ua, question=question2)
        self.assertIsNotNone(answer2)
        self.assertIsNotNone(answer2.userAnswer)
