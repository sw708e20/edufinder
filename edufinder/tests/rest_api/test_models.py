from django.test import TestCase
from django.db.utils import IntegrityError
from edufinder.rest_api.models import Question, Answer, UserAnswer, AnswerChoice, Education


class AnswerTests(TestCase):

    def test_answer_is_related_to_user_answer(self):
        question = Question.objects.create(
            en="What is the answer to life, the universe and everything?",
            da="What is the answer to life, the universe and everything?")
        user_answer = UserAnswer.objects.create(
            ip_addr="127.0.0.1", education=Education.objects.create(name="test education"))
        answer = Answer.objects.create(question=question, answer=AnswerChoice.YES,
                                       userAnswer=user_answer)

        self.assertEqual(answer, UserAnswer.objects.first().answer_set.first())

    def test_user_cannot_answer_same_question(self):
        question = Question.objects.create(
            en="What is the answer to life, the universe and everything?",
            da="What is the answer to life, the universe and everything?")
        user_answer = UserAnswer.objects.create(
            ip_addr="127.0.0.1", education=Education.objects.create(name="test education"))
        answer = Answer.objects.create(question=question,
                                       answer=AnswerChoice.YES, userAnswer=user_answer)

        with self.assertRaises(IntegrityError):
            answer = Answer.objects.create(question=question, answer=AnswerChoice.NO,
                                           userAnswer=user_answer)