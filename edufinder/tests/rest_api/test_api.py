from django.test import TestCase
from rest_framework.reverse import reverse
from rest_framework.test import APIRequestFactory
from rest_framework.test import force_authenticate
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from unittest.mock import MagicMock
import json

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
        views.get_nextquestion = MagicMock(return_value=Question.objects.get(question="question #1?").pk)

        response = self.client.post(
            f'/question/',
            data=json.dumps([
                {"id": 1, "answer": AnswerChoice.NO},
                {"id": 2, "answer": AnswerChoice.PROBABLY}]),
            content_type="application/json"
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['question'], "question #1?")


class RecommendApiTest(ApiTestBase):

    def test_POST_to_recommend_returns_educations(self):
        self.create_questions()
        self.create_educations()
        views.get_education_recommendation = MagicMock(return_value=Education.objects.filter(pk__in=[1,2,3]))
        questions = Question.objects.all()
        questions_list = [{"id": questions[i].pk, "answer": AnswerChoice.NO} for i in range(20)]

        response = self.client.post(
            f'/recommend/',
            data=json.dumps([
                questions_list,
            ]),
            content_type="application/json"
        )

        self.assertEqual(response.data[0]['id'], 1)


