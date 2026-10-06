from django.shortcuts import render


def index(request):
    return render(request, 'index.html')


def student_dashboard(request):
    return render(request, 'student/dashboard.html')


def teacher_dashboard(request):
    return render(request, 'teacher/dashboard.html')
