from django.test import TestCase
from rest_framework.reverse import reverse
from rest_framework.test import APIRequestFactory
from rest_framework.test import force_authenticate
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth.models import User
from django.core import management
import json

from edufinder.rest_api.models import Question, Answer, UserAnswer, AnswerChoice
from edufinder.rest_api.serializers import AnswerChoiceSerializer, EducationSerializer
from edufinder.rest_api.models import Question, Answer, UserAnswer, AnswerChoice, Education, EducationType
from edufinder.rest_api import views

class ApiTestBase(TestCase):

    def setUp(self):
        self.client = APIClient()
        user = User.objects.create_user(is_superuser=True, username="admin", password="admin")
        self.client.login(username="admin", password="admin")

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
        yes_value = AnswerChoiceSerializer().to_representation(AnswerChoice.YES)
        return [{"id": questions[i].pk, "answer": yes_value} for i in range(20)]

class SearchEducationTest(ApiTestBase):
    def test_search_no_query(self):
        self.create_educations()

        response = self.client.get(
            '/educations/'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {
            "q": [
                "This field is required."
            ]
        })

    def test_search_query(self):
        self.create_educations()

        response = self.client.get(
            '/educations/',
            data = {
                'q': 'Educatio'
            }
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 10)
    
    def test_search_ci_query(self):
        self.create_educations()

        response = self.client.get(
            '/educations/',
            data = {
                'q': 'educatio'
            }
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 10)
    
    def test_ignore_additional_params(self):
        self.create_educations()

        response = self.client.get(
            '/educations/',
            data = {
                'q': 'Educatio',
                'a': 123
            }
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 10)
    
    def test_no_result(self):
        self.create_educations()

        response = self.client.get(
            '/educations/',
            data = {
                'q': 'no_exist'
            }
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)
    
    def test_query_too_long(self):
        self.create_educations()

        response = self.client.get(
            '/educations/',
            data = {
                'q': 'b'*201
            }
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {
            "q": [
                "Ensure this field has no more than 200 characters."
            ]
        })

class QuestionApiTest(ApiTestBase):

    def test_POST_questions_returns_okay(self):
        self.create_questions()
        

        response = self.client.post(
            f'/question/',
            data=json.dumps([
                {"id": 1, "answer": AnswerChoice.NO},
                {"id": 2, "answer": AnswerChoice.PROBABLY}]),
            content_type="application/json"
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.data['en'])
        self.assertIsNotNone(response.data['da'])


class RecommendApiTest(ApiTestBase):
    def create_answerconsensus(self):
        management.call_command('create_consensus')

    def test_POST_to_recommend_returns_educations(self):
        questions_list = self.get_answered_questions()
        self.create_answerconsensus()

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


    def test_POST_questions_returns_incorrect_answertype(self):
        self.create_questions()
        

        response = self.client.post(
            f'/recommend/',
            data=json.dumps([
                {"id": 1, "answer": 'no'},
                {"id": 2, "answer": 1}]),
            content_type="application/json"
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, [{
            'answer': [
                'Incorrect type. Expected int, but got str'
            ]
        }, {}])


    def test_POST_questions_with_ints(self):
        self.create_questions()
        

        response = self.client.post(
            f'/recommend/',
            data=json.dumps([
                {"id": 1, "answer": -2},
                {"id": 2, "answer": 1}]),
            content_type="application/json"
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(response.data)
        


    def test_POST_questions_with_int_outofrange(self):
        self.create_questions()
        

        response = self.client.post(
            f'/recommend/',
            data=json.dumps([
                {"id": 1, "answer": -4},
                {"id": 2, "answer": 1}]),
            content_type="application/json"
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, [{
            'answer': [
                'Value of out range. Must be between -2 and 2'
            ]
        }, {}])


class GuessApiTest(ApiTestBase):

    def test_POST_correct_time_and_ip(self):
        from datetime import datetime, timezone, timedelta
        ip_addr = "127.0.0.1"
        question1 = Question.objects.create(en="Test question", da="Test question")
        question2 = Question.objects.create(en="Test question", da="Test question")
        self.create_educations()
        data = {"education": Education.objects.first().pk, "questions": 
                [
                    {"id": question1.pk, "answer": 2}, 
                    {"id": question2.pk, "answer": -2}]}

        response = self.client.post('/guess/',
            data=json.dumps(data),
            content_type="application/json",
            REMOTE_ADDR=ip_addr,
        )
        
        ua = UserAnswer.objects.first()

        self.assertIsNotNone(ua)
        self.assertEqual(response.status_code, 302)
        self.assertIsNotNone(ua.datetime)
        self.assertTrue(abs(ua.datetime - datetime.now(timezone.utc)) < timedelta(seconds=1))
        self.assertIsNotNone(ua.ip_addr)
        self.assertEqual(ua.ip_addr, ip_addr)

    def test_POST_saves_answers(self):
        questions_list = self.get_answered_questions()
        education = Education.objects.first()
        data = {"education": education.pk, "questions": questions_list}
        
        response = self.client.post('/guess/',
                    data=json.dumps(data),
                    content_type="application/json")

        self.assertEqual(UserAnswer.objects.all().count(), 1)
        self.assertListEqual([question['id'] for question in questions_list], [answer.pk for answer in Answer.objects.all()])
        self.assertEqual(UserAnswer.objects.first().education, Education.objects.first())
