import random

from django.shortcuts import redirect
from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.decorators import api_view
from rest_framework.decorators import parser_classes
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.parsers import JSONParser
from django_pivot.pivot import pivot
from django.db.models import Min
from math import sqrt
from .serializers import *
from typing import List
from .management.question_prioritization import get_question_tree


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


def get_random_question(previous_answers):
    return random.choice(list(set([x.id for x in Question.objects.all()]) -
                            set([x['id'] for x in previous_answers])))

def get_nextquestion(previous_answers: List[dict]):
    """
    Returns the primary key of the next question.

    Expected input format
        [ { id: int, answer: int }, ... ]
    """

    current_node = get_question_tree()

    if current_node is None:
        return get_random_question(previous_answers)

    for answer in previous_answers:
        if current_node is None:
            return get_random_question(previous_answers)
        current_node = current_node.children.get(answer['id'])

    return Question.objects.get(pk = current_node)


def get_education_recommendation(answers):
    """
    Returns a list of educations 
    """
    question_ids = [a['id'] for a in answers]
    answer_dict = {str(answer['id']): answer['answer'] for answer in answers}
    pivot_tab = pivot(AnswerConsensus.objects.filter(question_id__in=question_ids),
                      'education', 'question', 'answer', aggregation=Min)

    data_imp = {
        record['education']:
            sqrt(sum((answer_dict[str(_id)] - record[str(_id)])**2 for _id in question_ids))
        for record in pivot_tab}

    sorted_educations = {x[0]: x[1] for x in sorted(data_imp.items(), key=lambda x: x[1])[:10]}

    educations = Education.objects.filter(id__in=sorted_educations.keys()).all()[:10]

    return sorted(educations, key=lambda x: sorted_educations[x.id])


def get_educations(q: str):
    """
    Returns list of all educations
    """
    return [x for x in Education.objects.all() if q.lower() in x.name.lower()]


@api_view(['GET'])
def search_educations(request: Request):
    serializer = EducationSearchSerializer(data=request.GET)
    serializer.is_valid(raise_exception=True)

    educations = get_educations(serializer.data['q'])
    serializer = EducationSerializer(educations, many=True)
    return Response(serializer.data)


@api_view(['GET', 'POST'])
def next_question(request):
    if request.method == 'GET':
        questionpk = get_nextquestion([])
    else:
        serializer = AnswerSerializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)
        questionpk = get_nextquestion(serializer.data)

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


def log_recommender_input(request, serialized_data):
    ip = get_client_ip(request)
    education = Education.objects.get(pk=serialized_data['education'])

    answer = UserAnswer.objects.create(ip_addr=ip, education=education)
    for ans in serialized_data['questions']:
        ques = Question.objects.get(pk=ans['id'])
        Answer.objects.create(question=ques, answer=ans['answer'], userAnswer=answer)


@api_view(['POST'])
@parser_classes([JSONParser])
def recommend(request):
    serializer = AnswerSerializer(data=request.data, many=True)
    serializer.is_valid(raise_exception=True)
    recommendations = get_education_recommendation(serializer.data)
    serializer = EducationSerializer(recommendations, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@parser_classes([JSONParser])
def guess(request):
    serializer = GuessSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    log_recommender_input(request, serializer.data)
    
    return redirect("/")
