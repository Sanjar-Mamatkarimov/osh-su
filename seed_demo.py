# -*- coding: utf-8 -*-
"""
Создание демо-данных для проекта UniTrack.
Запуск: python seed_demo.py
"""
import os
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

import django
django.setup()

from apps.users.models import CustomUser, Group
from apps.teacher.models import Lecture, LabWork, StudentLabSubmission
from apps.student.models import StudentLectureStatus


def get_or_create_user(username, password, role, **kwargs):
    user, created = CustomUser.objects.get_or_create(
        username=username,
        defaults={'role': role, **kwargs}
    )
    if created or not user.has_usable_password():
        user.set_password(password)
        user.save()
    return user


def main():
    # --- Группы ---
    g1, _ = Group.objects.get_or_create(name='ИВТ-201')
    g2, _ = Group.objects.get_or_create(name='ИВТ-202')
    g3, _ = Group.objects.get_or_create(name='ПИ-301')

    # --- Пользователи ---
    teacher = get_or_create_user(
        'teacher', 'teacher', CustomUser.Role.TEACHER,
        first_name='Иван', last_name='Петров'
    )
    student = get_or_create_user(
        'student', 'student', CustomUser.Role.STUDENT,
        first_name='Аслан', last_name='Байбалаев', group=g1
    )
    s2 = get_or_create_user(
        'muhammad02', 'muhammad02', CustomUser.Role.STUDENT,
        first_name='Мухаммад', last_name='Алиев', group=g1
    )
    s3 = get_or_create_user(
        'timur03', 'timur03', CustomUser.Role.STUDENT,
        first_name='Тимур', last_name='Саидов', group=g1
    )
    s4 = get_or_create_user(
        'student2', 'student2', CustomUser.Role.STUDENT,
        first_name='Алина', last_name='Каримова', group=g2
    )

    # --- Лекции ---
    lectures_data = [
        ('Лекция №1', 'Введение в Django'),
        ('Лекция №2', 'Настройка проекта'),
        ('Лекция №3', 'Django Models'),
        ('Лекция №4', 'Django ORM'),
        ('Лекция №5', 'Views и URL-ы'),
        ('Лекция №6', 'Основы Django'),
        ('Лекция №7', 'Django Models'),
    ]
    lectures = []
    for title, desc in lectures_data:
        lec, _ = Lecture.objects.get_or_create(
            title=title, defaults={'description': desc}
        )
        lectures.append(lec)

    # --- Лабораторные работы ---
    labs_data = [
        ('Лабораторная №1', 'Введение в Django'),
        ('Лабораторная №2', 'Работа с Models'),
        ('Лабораторная №3', 'Django ORM'),
        ('Лабораторная №4', 'Views и маршруты'),
    ]
    labs = []
    for title, desc in labs_data:
        lab, _ = LabWork.objects.get_or_create(
            title=title, defaults={'description': desc}
        )
        labs.append(lab)

    # --- Статусы лекций (студент прочитал первые 6) ---
    for lec in lectures[:6]:
        StudentLectureStatus.objects.get_or_create(
            student=student, lecture=lec, defaults={'is_read': True}
        )

    # --- Отправленные работы ---
    submissions = [
        (student, labs[0], 'passed'),
        (student, labs[1], 'pending'),
        (s2, labs[0], 'passed'),
        (s2, labs[1], 'passed'),
        (s2, labs[2], 'passed'),
        (s3, labs[0], 'passed'),
        (s3, labs[1], 'pending'),
    ]
    for st, lab, status in submissions:
        StudentLabSubmission.objects.get_or_create(
            student=st, lab_work=lab,
            defaults={'status': status, 'comment': ''}
        )

    print('Демо-данные созданы.')
    print('Преподаватель: teacher / teacher')
    print('Студент:       student / student')
    print('Студенты:      muhammad02 / muhammad02, timur03 / timur03, student2 / student2')


if __name__ == '__main__':
    main()
