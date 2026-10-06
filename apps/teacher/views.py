from rest_framework.views import APIView
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from apps.users.models import CustomUser, Group
from apps.users.permissions import IsTeacherOrAdmin
from apps.users.serializers import GroupSerializer, UserSerializer
from .models import Lecture, LabWork, StudentLabSubmission
from apps.student.models import StudentLectureStatus
from .serializers import (
    StudentCreateSerializer, 
    GroupCreateSerializer, 
    RecentLabSubmissionSerializer,
    LabStatusUpdateSerializer,
    LectureCreateSerializer,
    LabWorkCreateSerializer
)

class DashboardStatsView(APIView):
    permission_classes = [IsTeacherOrAdmin]

    def get(self, request):
        total_groups = Group.objects.count()
        total_students = CustomUser.objects.filter(role=CustomUser.Role.STUDENT).count()
        pending_reviews = StudentLabSubmission.objects.filter(status=StudentLabSubmission.Status.PENDING).count()
        
        total_submissions = StudentLabSubmission.objects.count()
        passed_submissions = StudentLabSubmission.objects.filter(status=StudentLabSubmission.Status.PASSED).count()
        avg_progress = int((passed_submissions / total_submissions * 100)) if total_submissions > 0 else 0

        return Response({
            "total_groups": total_groups,
            "total_students": total_students,
            "pending_reviews": pending_reviews,
            "avg_progress": f"{avg_progress}%"
        })

class GroupCreateView(generics.CreateAPIView):
    queryset = Group.objects.all()
    serializer_class = GroupCreateSerializer
    permission_classes = [IsTeacherOrAdmin]

class GroupListView(APIView):
    permission_classes = [IsTeacherOrAdmin]

    def get(self, request):
        groups = Group.objects.all().order_by('name')
        data = [{
            "id": group.id,
            "name": group.name,
            "students_count": CustomUser.objects.filter(
                role=CustomUser.Role.STUDENT, group=group
            ).count()
        } for group in groups]
        return Response({"groups": data})

class CreateStudentView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = StudentCreateSerializer
    permission_classes = [IsTeacherOrAdmin]

class GroupStudentsView(APIView):
    permission_classes = [IsTeacherOrAdmin]

    def get(self, request, group_id):
        students = CustomUser.objects.filter(role=CustomUser.Role.STUDENT, group_id=group_id)

        group_lectures = Lecture.objects.filter(group_id=group_id) | Lecture.objects.filter(group__isnull=True)
        group_labs = LabWork.objects.filter(group_id=group_id) | LabWork.objects.filter(group__isnull=True)
        lectures = list(group_lectures.distinct().order_by('created_at').values('id', 'title'))
        labs = list(group_labs.distinct().order_by('created_at').values('id', 'title'))
        total_labs = len(labs)
        data = []
        for student in students:
            submissions = StudentLabSubmission.objects.filter(student=student)
            passed_labs = submissions.filter(status=StudentLabSubmission.Status.PASSED).count()
            progress = int((passed_labs / total_labs) * 100) if total_labs > 0 else 0

            lecture_statuses = {
                str(s['lecture_id']): s['is_read']
                for s in StudentLectureStatus.objects.filter(
                    student=student
                ).values('lecture_id', 'is_read')
            }
            lab_statuses = {
                str(s['lab_work_id']): s['status']
                for s in submissions.values('lab_work_id', 'status')
            }

            data.append({
                "id": student.id,
                "username": student.username,
                "full_name": student.get_full_name() or student.username,
                "progress": f"{progress}%",
                "lecture_statuses": lecture_statuses,
                "lab_statuses": lab_statuses,
                "submissions": RecentLabSubmissionSerializer(submissions, many=True).data
            })

        return Response({
            "students_count": students.count(),
            "lectures": lectures,
            "labs": labs,
            "students": data
        })

class PendingSubmissionsView(generics.ListAPIView):
    serializer_class = RecentLabSubmissionSerializer
    permission_classes = [IsTeacherOrAdmin]

    def get_queryset(self):
        return StudentLabSubmission.objects.filter(
            status=StudentLabSubmission.Status.PENDING
        ).select_related('student', 'lab_work').order_by('-submitted_at')

class VerifyLabView(APIView):
    permission_classes = [IsTeacherOrAdmin]

    def post(self, request, submission_id):
        action = request.data.get('action', 'approve')
        try:
            submission = StudentLabSubmission.objects.get(id=submission_id)

            if action == 'reject':
                submission.status = StudentLabSubmission.Status.LOCKED
                submission.save()
                return Response({"message": "Работа возвращена студенту на доработку"})

            submission.status = StudentLabSubmission.Status.PASSED
            submission.save()
            return Response({"message": "Работа успешно зачтена!"}, status=status.HTTP_200_OK)

        except StudentLabSubmission.DoesNotExist:
            return Response({"detail": "Работа не найдена"}, status=status.HTTP_404_NOT_FOUND)


class MaterialsView(APIView):
    """Список всех лекций и лабораторных работ (для кабинета преподавателя)."""
    permission_classes = [IsTeacherOrAdmin]

    def get(self, request):
        lectures = LectureCreateSerializer(
            Lecture.objects.select_related('group'), many=True
        ).data
        labs = LabWorkCreateSerializer(
            LabWork.objects.select_related('group'), many=True
        ).data
        return Response({"lectures": lectures, "labs": labs})


class CreateLectureView(generics.CreateAPIView):
    serializer_class = LectureCreateSerializer
    permission_classes = [IsTeacherOrAdmin]

    def get_queryset(self):
        return Lecture.objects.all()


class CreateLabWorkView(generics.CreateAPIView):
    serializer_class = LabWorkCreateSerializer
    permission_classes = [IsTeacherOrAdmin]

    def get_queryset(self):
        return LabWork.objects.all()