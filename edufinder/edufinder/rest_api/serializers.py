from django.contrib.auth.models import User, Group
from rest_framework import serializers
from .models import *


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['url', 'username', 'email', 'groups']


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ['url', 'name']


class QuestionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Question
        fields = ['id', 'en', 'da']


class EducationTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = EducationType
        fields = ['id', 'education', 'url', 'name']


class EducationSerializer(serializers.ModelSerializer):
    education_types = EducationTypeSerializer(many=True, read_only=True)

    class Meta:
        model = Education
        fields = ['id', 'name', 'description', 'education_types']


class AnswerSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=True)
    answer = serializers.ChoiceField(required=True, choices=AnswerChoice)


class GuessSerializer(serializers.Serializer):
    education = serializers.IntegerField(required=True)
    questions = serializers.ListField(allow_empty=False, child=AnswerSerializer())

    
class EducationSearchSerializer(serializers.Serializer):
    q = serializers.CharField(max_length=200)
