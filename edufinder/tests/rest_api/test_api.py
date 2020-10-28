from django.test import TestCase
from rest_framework.reverse import reverse
from rest_framework.test import APIRequestFactory
from rest_framework.test import force_authenticate
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth.models import User
from unittest.mock import MagicMock
import json

from edufinder.rest_api.models import Question, Answer, UserAnswer, AnswerChoice
from edufinder.rest_api.serializers import AnswerChoiceSerializer
from edufinder.rest_api.models import Question, Answer, UserAnswer, AnswerChoice, Education, EducationType
from edufinder.rest_api import views

class ApiTestBase(TestCase):

    def setUp(self):
        self.client = APIClient()
        user = User.objects.create_user(is_superuser=True, username="admin", password="admin")
        self.client.login(username="admin", password="admin")

    def create_questions(self):
        questions = [Question(question=f'question #{i}?') for i in range(30)]
        Question.objects.bulk_create(questions)

    def create_educations(self):
        educations = [Education(name = f'Education #{i}', description="description") for i in range(10)]
        Education.objects.bulk_create(educations)

        educations = Education.objects.all()
        education_types = [EducationType(education=educations[i], name=f'EducationType #{i}', url="http://example.com") for i in range(len(educations))]
        EducationType.objects.bulk_create(education_types)

class QuestionApiTest(ApiTestBase):

    def test_POST_questions_returns_new_question(self):
        self.create_questions()
        

        response = self.client.post(
            f'/question/',
            data=json.dumps([
                {"id": 1, "answer": AnswerChoice.NO},
                {"id": 2, "answer": AnswerChoice.PROBABLY}]),
            content_type="application/json"
        )
        
        self.assertEqual(response.status_code, 200)
        #self.assertEqual(response.data['question'], "question #1?")


class RecommendApiTest(ApiTestBase):

    def test_POST_to_recommend_returns_educations(self):
        self.create_questions()
        self.create_educations()
        
        questions = Question.objects.all()
        no_value = AnswerChoiceSerializer().to_representation(AnswerChoice.NO)
        questions_list = [{"id": questions[i].pk, "answer": no_value} for i in range(20)]

        response = self.client.post(
            f'/recommend/',
            data=json.dumps(
                questions_list,
            ),
            content_type="application/json"
        )
        self.assertIsNotNone(response.data)
        self.assertTrue(isinstance(response.data, list))
        self.assertEqual(response.data[0]['id'], 1)

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
    
    def test_POST_validator_not_json(self):
        response = self.client.post('/recommend/',
                    data="abba",
                    content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_POST_validator_bad_json(self):
        body = {
            "id": 1,
            "answer": 2
        }
        response = self.client.post('/recommend/',
                    data=json.dumps(body),
                    content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
