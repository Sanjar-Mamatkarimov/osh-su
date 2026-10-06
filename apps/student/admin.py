from django.contrib import admin
from .models import StudentLectureStatus

@admin.register(StudentLectureStatus)
class StudentLectureStatusAdmin(admin.ModelAdmin):
    list_display = ['student', 'lecture', 'is_read', 'read_at']
    list_filter = ['is_read', 'lecture']