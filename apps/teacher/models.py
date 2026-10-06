from django.db import models
from apps.users.models import CustomUser, Group

class Lecture(models.Model):
    title = models.CharField(max_length=255, verbose_name="Название лекции")
    description = models.TextField(blank=True, verbose_name="Описание")
    file = models.FileField(upload_to='lectures/', null=True, blank=True, verbose_name="Файл лекции")
    group = models.ForeignKey(
        Group,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='lectures',
        verbose_name="Учебная группа"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Лекция"
        verbose_name_plural = "Лекции"
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class LabWork(models.Model):
    title = models.CharField(max_length=255, verbose_name="Название лабораторной")
    description = models.TextField(blank=True, verbose_name="Описание/Задание")
    materials = models.FileField(
        upload_to='lab_materials/',
        null=True,
        blank=True,
        verbose_name="Материалы к работе"
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='lab_works',
        verbose_name="Учебная группа"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Лабораторная работа"
        verbose_name_plural = "Лабораторные работы"
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class StudentLabSubmission(models.Model):
    class Status(models.TextChoices):
        LOCKED = 'locked', 'Заблокировано'
        PENDING = 'pending', 'На проверке'
        PASSED = 'passed', 'Зачтено'

    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='lab_submissions', verbose_name="Студент")
    lab_work = models.ForeignKey(LabWork, on_delete=models.CASCADE, related_name='submissions', verbose_name="Лабораторная работа")
    submission_file = models.FileField(upload_to='student_labs/', null=True, blank=True, verbose_name="Файл решения")
    comment = models.TextField(blank=True, verbose_name="Комментарий студента")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING, verbose_name="Статус")
    submitted_at = models.DateTimeField(auto_now=True, verbose_name="Дата отправки")

    class Meta:
        verbose_name = "Отправленная лабораторная"
        verbose_name_plural = "Отправленные лабораторные"

    def __str__(self):
        return f"{self.student.get_full_name()} - {self.lab_work.title} ({self.get_status_display()})"