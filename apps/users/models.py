from django.db import models
from django.contrib.auth.models import AbstractUser

class Group(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name="Название группы")

    class Meta:
        verbose_name = "Учебная группа"
        verbose_name_plural = "Учебные группы"

    def __str__(self):
        return self.name


class CustomUser(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = 'admin', 'Администратор'
        TEACHER = 'teacher', 'Преподаватель'
        STUDENT = 'student', 'Студент'

    role = models.CharField(
        max_length=20, 
        choices=Role.choices, 
        default=Role.STUDENT,
        verbose_name="Роль"
    )
    group = models.ForeignKey(
        Group, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name="students",
        verbose_name="Учебная группа"
    )
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True, verbose_name="Аватар")

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.username}) - {self.get_role_display()}"
    
    
