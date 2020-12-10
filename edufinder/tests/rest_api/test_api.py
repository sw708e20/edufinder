from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth.models import User
from django.core import management
from edufinder.rest_api.models import Question, Answer, UserAnswer, AnswerChoice, Education, EducationType, AnswerConsensus
import json
from django.core.cache import cache

from .test_base import TestBase
from edufinder.rest_api.serializers import EducationSerializer
from edufinder.rest_api.models import Question, Answer, UserAnswer, AnswerChoice, Education, EducationType

class ApiTestBase(TestBase):

    def setUp(self):
        self.client = APIClient()
        user = User.objects.create_user(is_superuser=True, username="admin", password="admin")
        self.client.login(username=user.username, password=user.password)

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
            data={
                'q': 'Educatio'
            }
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 10)

    def test_search_ci_query(self):
        self.create_educations()

        response = self.client.get(
            '/educations/',
            data={
                'q': 'educatio'
            }
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 10)

    def test_ignore_additional_params(self):
        self.create_educations()

        response = self.client.get(
            '/educations/',
            data={
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
            data={
                'q': 'no_exist'
            }
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_query_too_long(self):
        self.create_educations()

        response = self.client.get(
            '/educations/',
            data={
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

    def test_POST_get_the_next_question(self):
        question1 = Question.objects.create(en=f'question #1?', da=f'question #1?')
        question2 = Question.objects.create(en=f'question #2?', da=f'question #2?')
        question3 = Question.objects.create(en=f'question #3?', da=f'question #3?')
        response = self.client.post(
            f'/question/',
            data=json.dumps([
                {"id": question1.pk, "answer": AnswerChoice.NO}]),
            content_type="application/json"
        )

        response = self.client.post(
            f'/question/',
            data=json.dumps([
                {"id": question1.pk, "answer": AnswerChoice.NO},
                {"id": question2.pk, "answer": AnswerChoice.YES}]),
            content_type="application/json"
        )

        self.assertEqual(response.data['id'], question3.pk)

    def test_POST_tree_has_been_created(self):
        self.create_user_answer()
        questions = Question.objects.all()
        response = self.client.post(
            f'/question/',
            data=json.dumps([
                {"id": questions[0].pk, "answer": AnswerChoice.NO},
                {"id": questions[1].pk, "answer": AnswerChoice.YES}]),
            content_type="application/json"
        )

        tree = cache.get('question_tree')

        self.assertIsNotNone(tree)
        
    def test_get_first_question(self):
        en_qst = 'First question.'
        da_qst = 'Første spørgsmål'
        Question.objects.create(en=en_qst, da=da_qst)
        response = self.client.get(
            '/question/'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['en'], en_qst)
        self.assertEqual(response.data['da'], da_qst)

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

    def test_POST_questions_returns_wrong_value(self):
        self.create_questions()

        response = self.client.post(
            f'/question/',
            data=json.dumps([
                {"id": 1, "answer": "123321"},
                {"id": 2, "answer": "321321"}]),
            content_type="application/json"
        )

        self.assertEqual(response.status_code, 400)

    def test_POST_questions_returns_field_required(self):
        self.create_questions()

        response = self.client.post(
            f'/question/',
            data=json.dumps([
                {"id": 1, "answe2r": "123321"},
                {"id": 2, "answe2r": "321321"}]),
            content_type="application/json"
        )

        self.assertEqual(response.status_code, 400)


class RecommendApiTest(ApiTestBase):

    def setUp(self):
        self.get_answered_questions()
        self.education1 = Education.objects.create(name='Test education', description='description')
        user_answer = UserAnswer.objects.create(education=self.education1, ip_addr='127.0.0.1')

        Answer.objects.bulk_create([Answer(question=qst, answer=AnswerChoice.NO, userAnswer=user_answer) for qst in Question.objects.all()])

        self.education2 = Education.objects.create(name='Test education2', description='desc2')
        user_answer2 = UserAnswer.objects.create(education=self.education2, ip_addr='127.0.0.1')

        Answer.objects.bulk_create([Answer(question=qst, answer=AnswerChoice.PROBABLY_NOT, userAnswer=user_answer2) for qst in Question.objects.all()])

        management.call_command('update_consensus')

    @staticmethod
    def search_recommend_list(list, name):
        for i in list:
            if i['name'] == name:
                return i
        return None

    def test_recommender_match(self):
        response = self.client.post(
            f'/recommend/',
            data=json.dumps(
                [{"id": q.id, "answer":AnswerChoice.NO} for q in Question.objects.all()],
            ),
            content_type="application/json"
        )
        self.assertIsNotNone(self.search_recommend_list(response.data, self.education1.name))

    def test_recommender_match_order(self):
        response = self.client.post(
            f'/recommend/',
            data=json.dumps(
                [{"id": q.id, "answer":AnswerChoice.NO} for q in Question.objects.all()],
            ),
            content_type="application/json"
        )
        self.assertEqual(response.data[0]['name'], self.education1.name)

    def test_recommender_match_order2(self):
        answers = [{"id": q.id, "answer":AnswerChoice.PROBABLY_NOT} for q in Question.objects.all()]
        # Skew the results towards education1
        answers[1] = {"id": answers[1]["id"], "answer": AnswerChoice.NO}
        response = self.client.post(
            f'/recommend/',
            data=json.dumps(answers),
            content_type="application/json"
        )
        self.assertEqual(response.data[0]['name'], self.education2.name)
        self.assertEqual(response.data[1]['name'], self.education1.name)

    def test_recommender_no_match(self):
        response = self.client.post(
            f'/recommend/',
            data=json.dumps(
                [{"id": q.id, "answer":AnswerChoice.DONT_KNOW} for q in Question.objects.all()],
            ),
            content_type="application/json"
        )
        self.assertIsNone(self.search_recommend_list(response.data, self.education1.name))

    def test_POST_to_recommend_returns_educations(self):
        questions_list = self.get_answered_questions()
        management.call_command('update_consensus')

        response = self.client.post(
            f'/recommend/',
            data=json.dumps(
                questions_list,
            ),
            content_type="application/json"
        )
        self.assertIsNotNone(response.data)
        self.assertTrue(isinstance(response.data, list))
        self.assertIsNotNone(response.data[0].get('id'))

    def test_POST_validator_no_json(self):
        response = self.client.post('/recommend/', data="abba", content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_POST_validator_bad_json(self):
        body = {
            "id": 1,
            "answer": 2
        }
        response = self.client.post('/recommend/', data=json.dumps(body),
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
                '"no" is not a valid choice.'
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
                '"-4" is not a valid choice.'
            ]
        }, {}])


class AnswerConsensusTest(ApiTestBase):

    def setUp(self):
        self.education1 = Education.objects.create(name='Abba', description='desc')
        self.education2 = Education.objects.create(name='Abba', description='desc')
        questions = [Question(en=f'question #{i}?', da=f'question #{i}?') for i in range(30)]
        Question.objects.bulk_create(questions)
        self.create_answers(self.education1, AnswerChoice.YES)
        self.create_answers(self.education1, AnswerChoice.YES)

        self.create_answers(self.education2, AnswerChoice.NO)
        self.create_answers(self.education2, AnswerChoice.NO)

    @staticmethod
    def create_answers(curr_edu, curr_ans):
        ua = UserAnswer.objects.create(education=curr_edu, ip_addr='127.0.0.1')
        Answer.objects.bulk_create([Answer(answer=curr_ans, question=q, userAnswer=ua) for q in Question.objects.all()])

    @staticmethod
    def count_answerconsensus(curr_edu, curr_ans):
        return AnswerConsensus.objects.filter(education=curr_edu, answer=curr_ans).count()

    def test_answer_consensus_created(self):
        self.assertEqual(AnswerConsensus.objects.count(), 0)
        management.call_command('update_consensus')
        self.assertNotEqual(AnswerConsensus.objects.count(), 0)

    def test_answer_consensus_most_popular(self):
        management.call_command('update_consensus')
        self.assertEqual(self.count_answerconsensus(self.education1, AnswerChoice.YES), Question.objects.count())

    def test_answer_consensus_most_popular_add1(self):
        self.create_answers(self.education1, AnswerChoice.NO)
        management.call_command('update_consensus')
        self.assertEqual(self.count_answerconsensus(self.education1, AnswerChoice.YES), Question.objects.count())

    def test_answer_consensus_equal_number_add2(self):
        self.create_answers(self.education1, AnswerChoice.NO)
        self.create_answers(self.education1, AnswerChoice.NO)
        management.call_command('update_consensus')
        self.assertEqual(self.count_answerconsensus(self.education1, AnswerChoice.YES), Question.objects.count())

    def test_answer_consensus_equal_number_add3(self):
        self.create_answers(self.education1, AnswerChoice.NO)
        self.create_answers(self.education1, AnswerChoice.NO)
        self.create_answers(self.education1, AnswerChoice.NO)
        management.call_command('update_consensus')
        self.assertEqual(self.count_answerconsensus(self.education1, AnswerChoice.NO), Question.objects.count())

    def test_answer_consensus_number_switchback(self):
        self.create_answers(self.education1, AnswerChoice.NO)
        self.create_answers(self.education1, AnswerChoice.NO)
        self.create_answers(self.education1, AnswerChoice.NO)
        management.call_command('update_consensus')
        self.assertEqual(self.count_answerconsensus(self.education1, AnswerChoice.NO), Question.objects.count())
        self.create_answers(self.education1, AnswerChoice.YES)
        management.call_command('update_consensus')
        self.assertEqual(self.count_answerconsensus(self.education1, AnswerChoice.YES), Question.objects.count())

    def test_answer_consensus_no_effect_edu2(self):
        self.create_answers(self.education2, AnswerChoice.NO)
        management.call_command('update_consensus')
        self.assertEqual(self.count_answerconsensus(self.education1, AnswerChoice.YES), Question.objects.count())

    def test_answer_consensus_default_dont_know(self):
        new_edu = Education.objects.create(name='Abba2', description='Abba2')
        management.call_command('update_consensus')
        self.assertEqual(self.count_answerconsensus(new_edu, AnswerChoice.DONT_KNOW), Question.objects.count())


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

        response = self.client.post('/guess/', data=json.dumps(data),
                                    content_type="application/json", REMOTE_ADDR=ip_addr)

        ua = UserAnswer.objects.first()

        self.assertIsNotNone(ua)
        self.assertEqual(response.status_code, 302)
        self.assertIsNotNone(ua.datetime)
        self.assertTrue(abs(ua.datetime - datetime.now(timezone.utc)) < timedelta(seconds=1))
        self.assertIsNotNone(ua.ip_addr)
        self.assertEqual(ua.ip_addr, ip_addr)

    def test_POST_correct_time_and_ip_fwd(self):
        from datetime import datetime, timezone, timedelta
        ip_addr = "127.0.0.1"
        fwd_ip = "8.8.8.8"
        question1 = Question.objects.create(en="Test question", da="Test question")
        question2 = Question.objects.create(en="Test question", da="Test question")
        self.create_educations()
        data = {"education": Education.objects.first().pk, "questions":
                [
                    {"id": question1.pk, "answer": 2},
                    {"id": question2.pk, "answer": -2}]}

        response = self.client.post(
            '/guess/', 
            data=json.dumps(data),
            content_type="application/json", 
            REMOTE_ADDR=ip_addr,
            HTTP_X_FORWARDED_FOR=fwd_ip
        )

        ua = UserAnswer.objects.first()

        self.assertIsNotNone(ua)
        self.assertEqual(response.status_code, 302)
        self.assertIsNotNone(ua.datetime)
        self.assertTrue(abs(ua.datetime - datetime.now(timezone.utc)) < timedelta(seconds=1))
        self.assertIsNotNone(ua.ip_addr)
        self.assertEqual(ua.ip_addr, fwd_ip)

    def test_POST_saves_answers(self):
        questions_list = self.get_answered_questions()
        education = Education.objects.first()
        data = {"education": education.pk, "questions": questions_list}

        response = self.client.post('/guess/', data=json.dumps(data),
                                    content_type="application/json")

        self.assertEqual(UserAnswer.objects.all().count(), 1)
        self.assertListEqual([question['id'] for question in questions_list],
                             [answer.pk for answer in Answer.objects.all()])
        self.assertEqual(UserAnswer.objects.first().education, Education.objects.first())


class DecsionTreeApiTest(ApiTestBase):

    def test_can_delete_cache(self):
        self.create_user_answer()
        questions = Question.objects.all()
        self.client.post(
            f'/question/',
            data=json.dumps([
                {"id": questions[0].pk, "answer": AnswerChoice.NO}]),
            content_type="application/json"
        )
    
        response = self.client.delete(
            f'/decision-tree/'
        )
        
        self.assertIsNone(cache.get('question_tree'))
        self.assertEqual(response.status_code, 200)
