from django.conf import settings
from django.db import models
from apps.teacher.models import Lecture

class StudentLectureStatus(models.Model):
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='lecture_statuses',
        verbose_name="Студент"
    )
    lecture = models.ForeignKey(
        Lecture, 
        on_delete=models.CASCADE, 
        related_name='student_statuses', 
        verbose_name="Лекция"
    )
    is_read = models.BooleanField(default=False, verbose_name="Изучено")
    read_at = models.DateTimeField(auto_now=True, verbose_name="Дата изучения")

    class Meta:
        verbose_name = "Статус лекции студента"
        verbose_name_plural = "Статусы лекций студентов"
        unique_together = ('student', 'lecture')

    def __str__(self):
        status = "Изучено" if self.is_read else "Не изучено"
        return f"{self.student.username} - {self.lecture.title} ({status})"