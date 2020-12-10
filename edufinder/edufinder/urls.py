"""edufinder URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import include, path
from rest_framework import routers
from edufinder.rest_api import views

router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'groups', views.GroupViewSet)
router.register(r'questions', views.QuestionViewSet)
router.register(r'education_types', views.EducationTypeViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('question/', views.next_question),
    path('recommend/', views.recommend),
    path('guess/', views.guess),
    path('educations/', views.search_educations),
    path('decision-tree/', views.decision_tree),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]