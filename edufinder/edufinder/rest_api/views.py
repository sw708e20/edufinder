from django.contrib.auth.models import User, Group
from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import *


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

def get_nextquestion(previous_answers):
    """
    Returns the primary key of the next question.
    """
    return 1

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
        questionpk = get_nextquestion(request.data)

    question = Question.objects.get(pk=questionpk)
    serializer = QuestionSerializer(question)
    return Response(serializer.data)

@api_view(['POST'])
def recommend(request):
    recommendations = get_education_recommendation(request.data)
    serializer = EducationSerializer(recommendations, many=True)
    return Response(serializer.data)