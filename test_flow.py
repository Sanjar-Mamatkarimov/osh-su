# -*- coding: utf-8 -*-
"""Полный цикл: студент сдаёт работу, учитель проверяет."""
import io
import json
import sys
import urllib.error
import urllib.request
import uuid

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE = 'http://127.0.0.1:8000'


def login(username, password):
    req = urllib.request.Request(
        BASE + '/api/users/login/',
        data=json.dumps({'username': username, 'password': password}).encode(),
        headers={'Content-Type': 'application/json'}
    )
    return json.load(urllib.request.urlopen(req))['token']


def api(url, token, method='GET', payload=None, form=None, files=None):
    headers = {'Authorization': 'Token ' + token}
    if form is not None or files:
        boundary = uuid.uuid4().hex
        body = b''
        for k, v in form.items():
            body += ('--%s\r\nContent-Disposition: form-data; name="%s"\r\n\r\n%s\r\n'
                     % (boundary, k, v)).encode('utf-8')
        for k, (fname, data) in files.items():
            body += ('--%s\r\nContent-Disposition: form-data; name="%s"; filename="%s"\r\n'
                     'Content-Type: application/octet-stream\r\n\r\n'
                     % (boundary, k, fname)).encode('utf-8')
            body += data + b'\r\n'
        body += ('--%s--\r\n' % boundary).encode()
        headers['Content-Type'] = 'multipart/form-data; boundary=' + boundary
        data = body
    elif payload is not None:
        headers['Content-Type'] = 'application/json'
        data = json.dumps(payload).encode('utf-8')
    else:
        data = None

    req = urllib.request.Request(BASE + url, data=data, headers=headers, method=method)
    try:
        return json.load(urllib.request.urlopen(req))
    except urllib.error.HTTPError as e:
        return {'ERR': e.code, 'body': e.read().decode('utf-8')}


def main():
    student = login('student', 'student')
    teacher = login('teacher', 'teacher')

    # 1. Студент сдаёт лабораторную №5 с файлом
    print('1. submit lab5:', api('/api/student/labs/submit/', student, 'POST',
          form={'lab_work': '5', 'comment': 'Готово, проверьте пожалуйста'},
          files={'submission_file': ('solution.py', b'print("hello forms")')}))

    # 2. Статус студента
    d = api('/api/student/dashboard/', student)
    print('2. student stats:', d['stats'])
    print('   lab5 status:', [l['status'] for l in d['lab_works'] if l['id'] == 5])

    # 3. Учитель видит работу в очереди
    pending = api('/api/teacher/submissions/pending/', teacher)
    print('3. pending:', [(p['id'], p['student_name'], p['lab_title'], bool(p['submission_file']))
                          for p in pending])
    target = next((p for p in pending if p['lab_title'] == 'Lab 5 Forms'), None)

    # 4. Учитель возвращает работу на доработку
    if target:
        print('4. reject:', api('/api/teacher/submissions/%d/verify/' % target['id'],
              teacher, 'POST', payload={'action': 'reject'}))
        d = api('/api/student/dashboard/', student)
        print('   lab5 after reject:',
              [l['status'] for l in d['lab_works'] if l['id'] == 5])

        # 5. Студент пересдаёт
        print('5. resubmit:', api('/api/student/labs/submit/', student, 'POST',
              form={'lab_work': '5', 'comment': 'Исправил'},
              files={'submission_file': ('solution_v2.py', b'print("fixed")')}))

    # 6. Учитель зачёл
    pending = api('/api/teacher/submissions/pending/', teacher)
    target = next((p for p in pending if p['lab_title'] == 'Lab 5 Forms'), None)
    if target:
        print('6. approve:', api('/api/teacher/submissions/%d/verify/' % target['id'],
              teacher, 'POST', payload={'action': 'approve'}))

    # 7. Итоговый статус студента
    d = api('/api/student/dashboard/', student)
    print('7. final stats:', d['stats'])
    print('   lab5 final:', [l['status'] for l in d['lab_works'] if l['id'] == 5])

    # 8. Учитель видит материалы
    m = api('/api/teacher/materials/', teacher)
    print('8. materials:', len(m['lectures']), 'lectures,', len(m['labs']), 'labs')

    # 9. Матрица группы
    g = api('/api/teacher/groups/1/students/', teacher)
    print('9. matrix group 1:', g['students_count'], 'students,',
          len(g['lectures']), 'lecture cols,', len(g['labs']), 'lab cols')


if __name__ == '__main__':
    main()
