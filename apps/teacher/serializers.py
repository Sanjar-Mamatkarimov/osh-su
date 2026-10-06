from rest_framework import serializers
from apps.users.models import CustomUser, Group
from apps.users.serializers import GroupSerializer, UserSerializer
from .models import Lecture, LabWork, StudentLabSubmission

class GroupCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['id', 'name']

class StudentCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=4)
    group_id = serializers.PrimaryKeyRelatedField(
        queryset=Group.objects.all(), 
        source='group', 
        write_only=True,
        required=True
    )

    class Meta:
        model = CustomUser
        fields = ['username', 'password', 'first_name', 'last_name', 'group_id']

    def create(self, validated_data):
        student = CustomUser.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            role=CustomUser.Role.STUDENT,
            group=validated_data.get('group')
        )
        return student

class RecentLabSubmissionSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.get_full_name', read_only=True)
    lab_title = serializers.CharField(source='lab_work.title', read_only=True)

    class Meta:
        model = StudentLabSubmission
        fields = ['id', 'student_name', 'lab_title', 'submission_file', 'comment', 'status', 'submitted_at']

class LabStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentLabSubmission
        fields = ['status']


class LectureCreateSerializer(serializers.ModelSerializer):
    group_id = serializers.PrimaryKeyRelatedField(
        queryset=Group.objects.all(),
        source='group',
        write_only=True,
        required=False,
        allow_null=True
    )
    group_name = serializers.CharField(source='group.name', read_only=True, default=None)

    class Meta:
        model = Lecture
        fields = ['id', 'title', 'description', 'file', 'group_id', 'group_name', 'created_at']


class LabWorkCreateSerializer(serializers.ModelSerializer):
    group_id = serializers.PrimaryKeyRelatedField(
        queryset=Group.objects.all(),
        source='group',
        write_only=True,
        required=False,
        allow_null=True
    )
    group_name = serializers.CharField(source='group.name', read_only=True, default=None)

    class Meta:
        model = LabWork
        fields = ['id', 'title', 'description', 'materials', 'group_id', 'group_name', 'created_at']