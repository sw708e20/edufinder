from django.contrib.auth.models import User, Group
from rest_framework import serializers
from rest_framework.serializers import ValidationError
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

class AnswerSerializer(serializers.BaseSerializer):
    def to_internal_value(self, value):
        if type(value) is not dict:
            raise serializers.ValidationError("Input is not a dictionary")

        for k, v in value.items():
            if type(k) is not str:
                raise serializers.ValidationError("Key is not string")
            if type(v) is not int:
                raise serializers.ValidationError("Value is not int")

        print(f"to_internal_value: {value}")
        return value

    def to_representation(self, instance):
        print(f"to_representation: {instance}")
        return instance


class GuessSerializer(serializers.Serializer):
    education = serializers.IntegerField(required=True)
    questions = serializers.ListField(allow_empty=False, child=AnswerSerializer())

    
class EducationSearchSerializer(serializers.Serializer):
    q = serializers.CharField(max_length=200)
