from django.urls import path
from .views import (
    DashboardStatsView,
    GroupCreateView,
    GroupListView,
    CreateStudentView,
    GroupStudentsView,
    PendingSubmissionsView,
    VerifyLabView,
    MaterialsView,
    CreateLectureView,
    CreateLabWorkView
)

urlpatterns = [
    path('stats/', DashboardStatsView.as_view(), name='teacher-stats'),
    path('groups/', GroupListView.as_view(), name='teacher-groups'),
    path('groups/create/', GroupCreateView.as_view(), name='teacher-create-group'),
    path('students/create/', CreateStudentView.as_view(), name='teacher-create-student'),
    path('groups/<int:group_id>/students/', GroupStudentsView.as_view(), name='teacher-group-students'),
    path('submissions/pending/', PendingSubmissionsView.as_view(), name='teacher-pending-submissions'),
    path('submissions/<int:submission_id>/verify/', VerifyLabView.as_view(), name='teacher-verify-lab'),
    path('materials/', MaterialsView.as_view(), name='teacher-materials'),
    path('lectures/create/', CreateLectureView.as_view(), name='teacher-create-lecture'),
    path('labs/create/', CreateLabWorkView.as_view(), name='teacher-create-lab'),
]