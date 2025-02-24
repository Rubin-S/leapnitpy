import random
from datetime import timedelta

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from website.models import Question, UserData, StudyMaterial, Subject, Course, Test, TestSubmitted, Chapter
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import login
import json
from django.db.models import Q
def home(request):
    if request.user.is_authenticated:
        return redirect('study')
    return render(request, 'index.html')


def team(request):
    return render(request, 'team.html')


def contactus(request):
    return render(request, 'contacts.html')


def study_page_route(request):
    if request.user.is_authenticated:
        email = request.user.username
        user = UserData.objects.get(email=email)
        try:
            course_name =user.course.name
            courses = Course.objects.filter(batch=user.batch, name=course_name)
        except:
            courses = Course.objects.filter(batch=user.batch)
        entire_dict = {}

        for course in courses:
            course_dict = {}
            for subject in course.subjects.all():
                subject_dict = {}
                for chapter in subject.chapters.all():
                    chapter_dict = []
                    for material in chapter.study_materials.all():
                        m = {}
                        m['url'] = material.file.url
                        m['desc'] = material.description
                        chapter_dict.append(m)
                    subject_dict[chapter.chapter_name] = {"chapter_dict" : chapter_dict, "key" : chapter.pk}
                course_dict[subject.subject_name] = subject_dict
            entire_dict[course.name] = course_dict
        return render(request, 'study.html', context={"entire_dict":entire_dict})
    return redirect('/login')


def login_route(request):
    if request.user.is_authenticated:
        return redirect('/study')
    if request.method == 'POST':
        username = request.POST['email']
        password = request.POST['password']
        print(username, password)
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('/study')
        else:
            messages.error(request, "Invalid username or password.")
    return render(request, 'login.html')


def signup_route(request):
    if request.user.is_authenticated:
        return redirect('/study')
    if request.method == 'POST':
        username = request.POST['email']
        password = request.POST['password']
        phno = request.POST['phno']
        batch = request.POST['batch']
        name = request.POST['name']
        course = request.POST['course']
        try:
            course = Course.objects.get(name=course, batch=batch)
        except:
            messages.error(request, f"We do not have currently course for {course} for batch {batch}")
        if User.objects.filter(username=username).exists():
            messages.error(request, "User already exists.")
        else:
            user = User.objects.create_user(username=username, password=password)
            login(request, user)
            UserData.objects.create(user=user, email=username, batch=batch, name=name, phone_number=phno, course=course)
            return redirect('/study')
    batch_names = Course.objects.values('batch').distinct().order_by('batch')
    course_name = Course.objects.values('name').distinct().order_by('name')
    batch_names_list = [batch['batch'] for batch in batch_names]
    course_name_list = [name['name'] for name in course_name]
    context = {"batch_names": batch_names_list, "course_name": course_name_list}
    return render(request, 'signup.html', context=context)

def logout_route(request):
    logout(request)
    return redirect('/')

def route_test(request, test_id):

    test = Test.objects.get(test_id=test_id)
    user = UserData.objects.get(user=request.user)
    existing_entry = TestSubmitted.objects.filter(user_email=user, test_id=test)
    if existing_entry.exists():
        return redirect('/study')
    if not test.accepting_response:
        return redirect('/profile')
    questions = test.question_list.all()
    questions_dict = {}

    for question in questions:
        q = {}
        q['question'] = question.question_text
        q['question_id'] = question.pk
        if question.question_file:
            q['question_file'] = question.question_file.url
        if question.type.lower() == "numerical":
            q['type'] = "numerical"
        else:
            q['type'] = question.type.lower()
            q['a'] = question.option_a
            q['b'] = question.option_b
            q['c'] = question.option_c
            q['d'] = question.option_d
            try:
                q['a_file'] = question.option_a_file.url
            except:
                pass
            try:
                q['b_file'] = question.option_b_file.url
            except:
                pass
            try:
                q['c_file'] = question.option_c_file.url
            except:
                pass
            try:
                q['d_file'] = question.option_d_file.url
            except:
                pass
        questions_dict[question.pk] = q
    d = {'test': {"questions": questions_dict, "time": int(test.duration.total_seconds()), "test_id": test.test_id}}
    return render(request, 'test.html', context=d)


@csrf_exempt
def submit_test(request, testId):
    if request.user.is_authenticated:
        if request.method == "POST":
            try:
                data = json.loads(request.body.decode('utf-8'))
                try:
                    test = Test.objects.get(test_id=testId)
                except:
                    return redirect('/profile')
                if not test.accepting_response:
                    return redirect('/profile')
                user = UserData.objects.get(user=request.user)
                existing_entry = TestSubmitted.objects.filter(user_email=user, test_id=test)
                if existing_entry.exists():
                    return JsonResponse({'message': 'Test submitted already'}, status=200)
                TestSubmitted.objects.update_or_create(user_email=user, test_id=test, json_response=data)
                return JsonResponse({'message': 'Test submitted successfully'}, status=200)
            except json.JSONDecodeError:
                return JsonResponse({'error': 'Invalid JSON'}, status=400)
            except Test.DoesNotExist:
                return JsonResponse({'error': 'Test not found'}, status=404)
            except UserData.DoesNotExist:
                return JsonResponse({'error': 'User not found'}, status=404)
        else:
            return JsonResponse({'error': 'Invalid method'}, status=405)
    else:
        return JsonResponse({'error': 'Unauthorized'}, status=401)

def profile(request):
    if request.user.is_authenticated:
        user = UserData.objects.get(user=request.user)
        username= user.name
        all_tests = Test.objects.filter(Q(owner=user) | Q(owner__isnull=True))
        testlist = []
        submittedtest = []
        for test in all_tests:
            t = {}
            t['test_id'] = test.test_id
            t['test_name'] = test.test_name
            attempted = False
            tt = TestSubmitted.objects.filter(user_email=user, test_id=test)
            t['available'] = test.accepting_response
            t['result_released'] = test.result_released
            if tt.exists():
                attempted = True
            t['attempted'] = attempted
            testlist.append(t)
            if attempted:
                submittedtest.append(t)


        return render(request, 'profile.html', context={'username': username, "testlist": testlist, "submittedtest": submittedtest})
    return redirect('/login')


def check(user_entry, actual):
    total = 0
    final_dict = {}
    for k,v in actual.items():
        ff = {}
        if user_entry.get(str(k), None) is not None:
            useranswer = user_entry.get(str(k), None)
            ff['your_answer'] = useranswer
            if v.get('type', None) == 'numerical':
                useranswer = float(useranswer)
                if useranswer<v.get('max_ans') and useranswer>v.get('min_ans'):
                    ff['status'] = "Correct"
                    ff['marks'] = v.get('marks_awarded')
                    total += ff['marks']
                else:
                    ff['status'] = "Incorrect"
                    ff['marks'] =-v.get('marks_deducted')
                    total += ff['marks']
                ff['correct_ans'] = f"Between {v.get('min_ans')} to {v.get('max_ans')} was acceptable range."
            else:
                if str(useranswer).lower() == v.get('answer').lower():
                    ff['status'] = "Correct"
                    ff['marks'] = v.get('marks_awarded')
                    total += ff['marks']
                else:
                    ff['status'] = "Incorrect"
                    ff['marks'] = -v.get('marks_deducted')
                    total += ff['marks']
                ff['correct_ans'] = v.get('answer').upper()
        else:
            ff['status'] = "Unattempted"
            ff['marks'] =0
            if v.get('type', None) == 'numerical':
                ff['correct_ans'] = f"Between {v.get('min_ans')} to {v.get('max_ans')} was acceptable range."
            else:
                ff['correct_ans'] = v.get('answer').upper()
        ff['question'] = v.get("question")
        ff['explanation_text'] = v.get("explanation_text")
        ff['question_file'] = v.get("question_file")
        ff['explanation_file'] = v.get("explanation_file")

        final_dict[k] = ff

    return final_dict, total

def analyse(request, test_id):
    if request.user.is_authenticated:
        user = UserData.objects.get(user=request.user)
        test = Test.objects.get(test_id=test_id)
        submission = TestSubmitted.objects.filter(user_email=user, test_id=test)
        if not submission.exists():
            return redirect('/profile')
        if not test.result_released:
            return redirect('/profile')
        tsb = TestSubmitted.objects.get(test_id=test, user_email=user)
        if tsb.analysis is not None:
            qna_list= tsb.analysis
            total = tsb.score
            context = {"qna": qna_list, "total": total}
            return render(request, 'analyse.html', context=context)
        questions = test.question_list.all()
        submission = submission[0]
        answer_dict = {}
        for question in questions:
            temp = {}
            temp['marks_awarded'] = question.marks_award
            temp['question'] = question.question_text
            temp['explanation_text'] = question.explanation
            try:
                temp['question_file'] = question.question_file.url
            except:
                pass
            try:
                temp['explanation_file'] = question.explanation_file.url
            except:
                pass
            temp['marks_deducted'] = question.marks_deduct
            if question.type =="numerical":
                temp['type'] = "numerical"
                temp['min_ans'] = question.correct_answer_numerical_min
                temp['max_ans'] = question.correct_answer_numerical_max
            else:
                temp['type'] = question.type.lower()
                temp['answer'] = question.correct_option.lower()
            answer_dict[question.pk] = temp
        qna, total = check(submission.json_response, answer_dict)
        qna_list = [{"id": key, **value} for key, value in qna.items()]
        tsb = TestSubmitted.objects.get(test_id=test, user_email=user)
        tsb.analysis = qna_list
        tsb.score = total
        tsb.save()
        context = {"qna": qna_list, "total": total}
        return render(request, 'analyse.html', context=context)


def create_test(request, chapter_id):
    chapter = Chapter.objects.get(pk=chapter_id)
    questions = Question.objects.filter(chapter=chapter, visible=True)
    duration = len(list(questions))*5*60
    duration = timedelta(seconds=duration)
    user = UserData.objects.get(user=request.user)
    test = Test.objects.create(owner=user, test_name=f"Your Test for {chapter}", duration=duration, result_released=True, accepting_response=True)
    test.question_list.set(questions)
    return redirect(f'/test/{test.test_id}')
