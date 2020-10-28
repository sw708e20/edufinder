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
        fields = ['id', 'question']


class EducationTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = EducationType
        fields = ['id', 'education', 'url', 'name']


class EducationSerializer(serializers.ModelSerializer):
    education_types = EducationTypeSerializer(many=True, read_only=True)

    class Meta:
        model = Education
        fields = ['id', 'name', 'description', 'education_types']

class AnswerChoiceSerializer(serializers.Field):
    """
    Choices are serialized into the integer value
    """
    conversion_dict = {
        "2": AnswerChoice.YES,
        "1": AnswerChoice.PROBABLY,
        "0": AnswerChoice.DONT_KNOW,
        "-1": AnswerChoice.PROBABLY_NOT,
        "-2": AnswerChoice.NO,
    }

    def to_representation(self, value):
        for key, val in self.conversion_dict.items():
            if val == value:
                return int(key)
        raise ValueError(f'The value "{value}" cannot be converted')
    
    def to_internal_value(self, data):
        if not isinstance(data, int):
            raise ValidationError(f'Incorrect type. Expected int, but got {type(data).__name__}')
        if data > 2 or data < -2:
            raise ValidationError("Value of out range. Must be between -2 and 2")
        return self.conversion_dict[str(data)]

class AnswerSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=True)
    answer = AnswerChoiceSerializer(required=True)