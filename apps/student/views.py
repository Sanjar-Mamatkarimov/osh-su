from rest_framework.views import APIView
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from apps.teacher.models import Lecture, LabWork, StudentLabSubmission
from .models import StudentLectureStatus
from .serializers import (
    StudentLectureSerializer, 
    StudentLabSerializer, 
    SubmitLabSerializer
)

class StudentDashboardView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        student = request.user
        student_group = getattr(student, 'group', None)

        group_lectures = (Lecture.objects.filter(group=student_group)
                          | Lecture.objects.filter(group__isnull=True)).distinct()
        group_labs = (LabWork.objects.filter(group=student_group)
                      | LabWork.objects.filter(group__isnull=True)).distinct()

        total_labs = group_labs.count()
        passed_labs = StudentLabSubmission.objects.filter(
            student=student, status=StudentLabSubmission.Status.PASSED,
            lab_work__in=group_labs
        ).count()
        pending_labs = StudentLabSubmission.objects.filter(
            student=student, status=StudentLabSubmission.Status.PENDING,
            lab_work__in=group_labs
        ).count()

        total_lectures = group_lectures.count()
        read_lectures = StudentLectureStatus.objects.filter(
            student=student, is_read=True, lecture__in=group_lectures
        ).count()

        overall_progress = int((passed_labs / total_labs) * 100) if total_labs > 0 else 0

        lectures = group_lectures.order_by('-created_at')[:5]
        labs = group_labs

        return Response({
            "student_info": {
                "first_name": student.first_name or student.username,
                "group_name": student.group.name if student.group else "Без группы"
            },
            "stats": {
                "labs_completed": f"{passed_labs}/{total_labs}",
                "lectures_completed": f"{read_lectures}/{total_lectures}",
                "pending_count": pending_labs,
                "overall_progress": f"{overall_progress}%",
                "remaining_labs": total_labs - passed_labs
            },
            "recent_lectures": StudentLectureSerializer(lectures, many=True, context={'request': request}).data,
            "lab_works": StudentLabSerializer(labs, many=True, context={'request': request}).data
        })

class MarkLectureReadView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, lecture_id):
        try:
            lecture = Lecture.objects.get(id=lecture_id)
            obj, created = StudentLectureStatus.objects.get_or_create(
                student=request.user, 
                lecture=lecture
            )
            obj.is_read = True
            obj.save()
            return Response({"message": "Статус лекции обновлен на 'Изучено'"}, status=status.HTTP_200_OK)
        except Lecture.DoesNotExist:
            return Response({"detail": "Лекция не найдена"}, status=status.HTTP_404_NOT_FOUND)

class SubmitLabWorkView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = SubmitLabSerializer(data=request.data)
        if serializer.is_valid():
            lab_work = serializer.validated_data['lab_work']
            defaults = {
                'comment': serializer.validated_data.get('comment', ''),
                'status': StudentLabSubmission.Status.PENDING
            }
            if serializer.validated_data.get('submission_file'):
                defaults['submission_file'] = serializer.validated_data['submission_file']

            StudentLabSubmission.objects.update_or_create(
                student=request.user,
                lab_work=lab_work,
                defaults=defaults
            )
            return Response({"message": "Лабораторная работа отправлена на проверку!"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)