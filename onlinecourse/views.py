from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.views import generic
import logging

from .models import Course, Enrollment, Choice, Submission

logger = logging.getLogger(__name__)


def registration_request(request):
    context = {}
    if request.method == 'GET':
        return render(request, 'onlinecourse/user_registration_bootstrap.html', context)
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('psw', '')
        first_name = request.POST.get('firstname', '').strip()
        last_name = request.POST.get('lastname', '').strip()
        if not username or not password:
            context['message'] = 'Username and password are required.'
            return render(request, 'onlinecourse/user_registration_bootstrap.html', context)
        if User.objects.filter(username=username).exists():
            context['message'] = 'User already exists.'
            return render(request, 'onlinecourse/user_registration_bootstrap.html', context)
        user = User.objects.create_user(username=username, first_name=first_name,
                                        last_name=last_name, password=password)
        login(request, user)
        return redirect('onlinecourse:index')
    return redirect('onlinecourse:index')


def login_request(request):
    context = {}
    if request.method == 'POST':
        username = request.POST.get('username', '')
        password = request.POST.get('psw', '')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('onlinecourse:index')
        context['message'] = 'Invalid username or password.'
    return render(request, 'onlinecourse/user_login_bootstrap.html', context)


def logout_request(request):
    logout(request)
    return redirect('onlinecourse:index')


def check_if_enrolled(user, course):
    return bool(user.is_authenticated and Enrollment.objects.filter(user=user, course=course).exists())


class CourseListView(generic.ListView):
    template_name = 'onlinecourse/course_list_bootstrap.html'
    context_object_name = 'course_list'

    def get_queryset(self):
        courses = Course.objects.order_by('-total_enrollment')[:10]
        for course in courses:
            course.is_enrolled = check_if_enrolled(self.request.user, course)
        return courses


class CourseDetailView(generic.DetailView):
    model = Course
    template_name = 'onlinecourse/course_details_bootstrap.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_enrolled'] = check_if_enrolled(self.request.user, self.object)
        return context


def enroll(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    if request.user.is_authenticated and not check_if_enrolled(request.user, course):
        Enrollment.objects.create(user=request.user, course=course, mode='honor')
        course.total_enrollment += 1
        course.save(update_fields=['total_enrollment'])
    return HttpResponseRedirect(reverse('onlinecourse:course_details', args=(course.id,)))


def extract_answers(request):
    """Collect selected choice IDs posted by the exam form."""
    submitted_answers = []
    for key, value in request.POST.items():
        if key.startswith('choice_'):
            try:
                submitted_answers.append(int(value))
            except (TypeError, ValueError):
                continue
    return submitted_answers


@login_required
def submit(request, course_id):
    if request.method != 'POST':
        return HttpResponseRedirect(reverse('onlinecourse:course_details', args=(course_id,)))

    course = get_object_or_404(Course, pk=course_id)
    enrollment = get_object_or_404(Enrollment, user=request.user, course=course)
    selected_ids = extract_answers(request)
    submission = Submission.objects.create(enrollment=enrollment)

    # Only save choices that belong to this course's questions.
    valid_choices = Choice.objects.filter(
        id__in=selected_ids,
        question__course=course,
    )
    submission.choices.set(valid_choices)
    return redirect('onlinecourse:show_exam_result', course_id=course.id,
                    submission_id=submission.id)


@login_required
def show_exam_result(request, course_id, submission_id):
    course = get_object_or_404(Course, pk=course_id)
    submission = get_object_or_404(
        Submission,
        pk=submission_id,
        enrollment__user=request.user,
        enrollment__course=course,
    )
    selected_ids = list(submission.choices.values_list('id', flat=True))
    questions = []
    score = 0
    possible_score = 0

    for question in course.question_set.all().prefetch_related('choice_set'):
    possible_score += question.grade
    correct = question.is_get_score(selected_ids)

    if correct:
        score += question.grade

    questions.append({
        'question': question,
        'choices': question.choice_set.all(),
        'correct': correct,
    })

    grade = round((score / possible_score) * 100) if possible_score else 0
    context = {
        'course': course,
        'submission': submission,
        'questions': questions,
        'question_results': questions,
        'selected_ids': selected_ids,
        'score': score,
        'possible_score': possible_score,
        'grade': grade,
    }
    return render(request, 'onlinecourse/exam_result_bootstrap.html', context)
