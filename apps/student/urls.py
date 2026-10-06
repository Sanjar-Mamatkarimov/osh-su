from django.urls import path
from .views import (
    StudentDashboardView, 
    MarkLectureReadView, 
    SubmitLabWorkView
)

urlpatterns = [
    path('dashboard/', StudentDashboardView.as_view(), name='student-dashboard'),
    path('lectures/<int:lecture_id>/read/', MarkLectureReadView.as_view(), name='student-lecture-read'),
    path('labs/submit/', SubmitLabWorkView.as_view(), name='student-lab-submit'),
]