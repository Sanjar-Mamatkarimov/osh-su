from rest_framework import serializers
from apps.teacher.models import Lecture, LabWork, StudentLabSubmission
from apps.student.models import StudentLectureStatus

class StudentLectureSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField()

    class Meta:
        model = Lecture
        fields = ['id', 'title', 'description', 'file', 'created_at', 'status']

    def get_status(self, obj):
        student = self.context.get('request').user
        status_obj = StudentLectureStatus.objects.filter(student=student, lecture=obj).first()
        return "Изучено" if (status_obj and status_obj.is_read) else "Не изучено"

class StudentLabSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField()
    submission_id = serializers.SerializerMethodField()

    class Meta:
        model = LabWork
        fields = ['id', 'title', 'description', 'materials', 'created_at', 'status', 'submission_id']

    def get_status(self, obj):
        student = self.context.get('request').user
        submission = StudentLabSubmission.objects.filter(student=student, lab_work=obj).first()
        if not submission:
            return "Не сдано"

        status_map = {
            'pending': 'На проверке',
            'passed': 'Зачтено',
            'locked': 'На доработку'
        }
        return status_map.get(submission.status, 'Не сдано')

    def get_submission_id(self, obj):
        student = self.context.get('request').user
        submission = StudentLabSubmission.objects.filter(student=student, lab_work=obj).first()
        return submission.id if submission else None

class SubmitLabSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentLabSubmission
        fields = ['lab_work', 'submission_file', 'comment']