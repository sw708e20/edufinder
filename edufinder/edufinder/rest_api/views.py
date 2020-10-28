import random

from django.contrib.auth.models import User, Group
from rest_framework import viewsets
from rest_framework import status
from rest_framework import permissions
from rest_framework.decorators import api_view
from rest_framework.decorators import parser_classes
from rest_framework.response import Response
from rest_framework.parsers import JSONParser
from .serializers import *
from typing import List
import json


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated]


class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    permission_classes = [permissions.IsAuthenticated]


class EducationViewSet(viewsets.ModelViewSet):
    queryset = Education.objects.all()
    serializer_class = EducationSerializer
    permission_classes = [permissions.IsAuthenticated]


class EducationTypeViewSet(viewsets.ModelViewSet):
    queryset = EducationType.objects.all()
    serializer_class = EducationTypeSerializer
    permission_classes = [permissions.IsAuthenticated]


def get_firstquestion():
    """
    Returns the primary key of the first question asked.
    """
    return 1


def get_nextquestion(previous_answers: List[dict]):
    """
    Returns the primary key of the next question.

    Expected input format
        [ { id: int, question: str, answer: int }, ... ]
    """
    return random.choice(list(set([x.id for x in Question.objects.all()]) -
                              set([x['id'] for x in previous_answers])))


def get_education_recommendation(answers):
    """
    Returns a list of educations 
    """
    return Education.objects.all()[:10]


@api_view(['GET', 'POST'])
def next_question(request):
    if request.method == 'GET':
        questionpk = get_firstquestion()
    else:
        Answer.objects.create(
            question=Question.objects.get(pk=request.POST['question']), 
            userAnswer=UserAnswer.objects.get(pk=request.POST['userAnswer']),
            answer=request.POST['answer'])
        questionpk = get_nextquestion(request.data)

    question = Question.objects.get(pk=questionpk)
    serializer = QuestionSerializer(question)
    return Response(serializer.data)

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def parse_answer(input):
    if input == 2:
        result = AnswerChoice.YES
    elif input == 1:
        result = AnswerChoice.PROBABLY
    elif input == 0:
        result = AnswerChoice.DONT_KNOW
    elif input == -1:
        result = AnswerChoice.PROBABLY_NOT
    elif input == -2:
        result = AnswerChoice.NO
    return result

def log_recommender_input(request, serialized_data):
    ip = get_client_ip(request)
    answer = UserAnswer.objects.create(ip_addr=ip)
    for ans in serialized_data:
        ques = Question.objects.get(pk=ans['id'])
        parsed_answer = parse_answer(ans['answer'])
        Answer.objects.create(question=ques, answer=parsed_answer, userAnswer=answer)


@api_view(['POST'])
@parser_classes([JSONParser])
def recommend(request):
    serializer = AnswerSerializer(data=request.data, many=True)
    serializer.is_valid(raise_exception=True)
    log_recommender_input(request, serializer.data)
    recommendations = get_education_recommendation(request.data)
    serializer = EducationSerializer(recommendations, many=True)
    return Response(serializer.data)
