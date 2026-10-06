from django.contrib import admin
from .models import Lecture, LabWork, StudentLabSubmission

@admin.register(Lecture)
class LectureAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'created_at']

@admin.register(LabWork)
class LabWorkAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'created_at']

@admin.register(StudentLabSubmission)
class StudentLabSubmissionAdmin(admin.ModelAdmin):
    list_display = ['id', 'student', 'lab_work', 'status', 'submitted_at']
    list_filter = ['status', 'lab_work']