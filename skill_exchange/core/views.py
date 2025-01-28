# core/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import CustomUserCreationForm
from .models import UserSkill
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Skill, UserSkill, Session, User
from .forms import UserSkillForm, SessionForm
from django.db.models import Q
from django.utils import timezone
from django.db.models import Avg
from .forms import ReviewForm
from django.contrib.auth import logout
from .models import Message
from .forms import MessageForm

def home(request):
    return render(request, 'core/home.html')

def logout_view(request):
    logout(request)
    messages.success(request, 'You have been successfully logged out.')
    return redirect('home')

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Registration successful. Please login.')
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'core/register.html', {'form': form})

@login_required
def dashboard(request):
    teaching_skills = UserSkill.objects.filter(user=request.user, is_teaching=True)
    learning_skills = UserSkill.objects.filter(user=request.user, is_teaching=False)
    return render(request, 'core/dashboard.html', {
        'teaching_skills': teaching_skills,
        'learning_skills': learning_skills
    })

@login_required
def skill_list(request):
    teaching_skills = UserSkill.objects.filter(user=request.user, is_teaching=True)
    learning_skills = UserSkill.objects.filter(user=request.user, is_teaching=False)
    available_skills = Skill.objects.all()
    
    context = {
        'teaching_skills': teaching_skills,
        'learning_skills': learning_skills,
        'available_skills': available_skills,
    }
    return render(request, 'core/skill_list.html', context)

@login_required
def add_skill(request):
    if request.method == 'POST':
        form = UserSkillForm(request.POST)
        if form.is_valid():
            user_skill = form.save(commit=False)
            user_skill.user = request.user
            
            # Check if the user already has this skill in the same teaching/learning category
            existing_skill = UserSkill.objects.filter(
                user=request.user,
                skill=user_skill.skill,
                is_teaching=user_skill.is_teaching
            ).first()
            
            if existing_skill:
                messages.error(request, 'You already have this skill in your profile!')
                return redirect('skill_list')
                
            user_skill.save()
            messages.success(request, 'Skill added successfully!')
            return redirect('skill_list')
    else:
        form = UserSkillForm()
    
    return render(request, 'core/add_skill.html', {'form': form})

@login_required
def delete_user_skill(request, skill_id):
    user_skill = get_object_or_404(UserSkill, id=skill_id, user=request.user)
    user_skill.delete()
    messages.success(request, 'Skill removed successfully!')
    return redirect('skill_list')



@login_required
def find_matches(request):
    # Get the skills the user wants to learn
    learning_skills = UserSkill.objects.filter(
        user=request.user,
        is_teaching=False
    ).values_list('skill_id', flat=True)

    # Find all teachers for these skills
    potential_teachers = UserSkill.objects.select_related('user', 'skill').filter(
        skill_id__in=learning_skills,
        is_teaching=True
    ).exclude(user=request.user)

    # Group teachers by skill
    teachers_by_skill = {}
    for teacher_skill in potential_teachers:
        skill_name = teacher_skill.skill.name
        if skill_name not in teachers_by_skill:
            teachers_by_skill[skill_name] = []
        
        # Add teacher info
        teachers_by_skill[skill_name].append({
            'user': teacher_skill.user,
            'proficiency': teacher_skill.get_proficiency_display(),
            'user_id': teacher_skill.user.id,
            'skill_id': teacher_skill.skill.id
        })

    context = {
        'teachers_by_skill': teachers_by_skill,
    }
    
    return render(request, 'core/find_matches.html', context)


@login_required
def request_session(request, teacher_id, skill_id):
    teacher = get_object_or_404(User, id=teacher_id)
    skill = get_object_or_404(Skill, id=skill_id)
    
    if request.method == 'POST':
        form = SessionForm(request.POST)
        if form.is_valid():
            session = form.save(commit=False)
            session.teacher = teacher
            session.student = request.user
            session.skill = skill
            
            # Validate that scheduled time is in the future
            if session.scheduled_time <= timezone.now():
                messages.error(request, 'Please select a future date and time.')
                return render(request, 'core/request_session.html', {'form': form, 'teacher': teacher, 'skill': skill})
            
            session.save()
            messages.success(request, 'Session request sent successfully!')
            return redirect('session_list')
    else:
        form = SessionForm(initial={'skill': skill})
    
    return render(request, 'core/request_session.html', {
        'form': form,
        'teacher': teacher,
        'skill': skill
    })

@login_required
def session_list(request):
    # Get all sessions where the user is either teacher or student
    teaching_sessions = Session.objects.filter(teacher=request.user)
    learning_sessions = Session.objects.filter(student=request.user)
    
    return render(request, 'core/session_list.html', {
        'teaching_sessions': teaching_sessions,
        'learning_sessions': learning_sessions
    })

@login_required
def session_detail(request, session_id):
    session = get_object_or_404(Session, id=session_id)
    
    # Ensure user is either teacher or student of the session
    if request.user not in [session.teacher, session.student]:
        messages.error(request, 'You do not have permission to view this session.')
        return redirect('session_list')
    
    return render(request, 'core/session_detail.html', {'session': session})

@login_required
def update_session_status(request, session_id):
    if request.method == 'POST':
        session = get_object_or_404(Session, id=session_id)
        new_status = request.POST.get('status')
        
        # Verify user has permission to update status
        if request.user != session.teacher:
            messages.error(request, 'Only the teacher can update the session status.')
            return redirect('session_detail', session_id=session_id)
        
        if new_status in dict(Session.STATUS_CHOICES):
            session.status = new_status
            session.save()
            messages.success(request, 'Session status updated successfully!')
        else:
            messages.error(request, 'Invalid status provided.')
            
    return redirect('session_detail', session_id=session_id)



@login_required
def add_review(request, session_id):
    session = get_object_or_404(Session, id=session_id)
    
    # Verify that the user is the student of this session
    if request.user != session.student:
        messages.error(request, 'Only students can review their sessions.')
        return redirect('session_detail', session_id=session_id)
    
    # Verify that the session is completed
    if session.status != 'COMPLETED':
        messages.error(request, 'You can only review completed sessions.')
        return redirect('session_detail', session_id=session_id)
    
    # Check if review already exists
    if hasattr(session, 'review'):
        messages.error(request, 'You have already reviewed this session.')
        return redirect('session_detail', session_id=session_id)
    
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.session = session
            review.reviewer = request.user
            review.save()
            messages.success(request, 'Thank you for your review!')
            return redirect('session_detail', session_id=session_id)
    else:
        form = ReviewForm()
    
    return render(request, 'core/add_review.html', {
        'form': form,
        'session': session
    })

@login_required
def teacher_reviews(request, teacher_id):
    teacher = get_object_or_404(User, id=teacher_id)
    
    # Get all completed sessions where this user was the teacher
    completed_sessions = Session.objects.filter(
        teacher=teacher,
        status='COMPLETED',
        review__isnull=False
    ).select_related('review', 'student', 'skill')
    
    # Calculate average rating
    average_rating = completed_sessions.aggregate(
        avg_rating=Avg('review__rating')
    )['avg_rating']
    
    return render(request, 'core/teacher_reviews.html', {
        'teacher': teacher,
        'sessions': completed_sessions,
        'average_rating': average_rating
    })



@login_required
def message_list(request):
    messages = Message.objects.filter(receiver=request.user)
    return render(request, 'core/messages/inbox.html', {'messages': messages})

@login_required
def sent_messages(request):
    messages = Message.objects.filter(sender=request.user)
    return render(request, 'core/messages/sent.html', {'messages': messages})

@login_required
def compose_message(request, receiver_id):
    receiver = get_object_or_404(User, id=receiver_id)
    
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = request.user
            message.receiver = receiver
            message.save()
            messages.success(request, 'Message sent successfully!')
            return redirect('message_list')
    else:
        form = MessageForm()
    
    return render(request, 'core/messages/compose.html', {
        'form': form,
        'receiver': receiver
    })

@login_required
def message_detail(request, message_id):
    message = get_object_or_404(Message, id=message_id)
    
    # Verify user has permission to view this message
    if request.user not in [message.sender, message.receiver]:
        messages.error(request, 'You do not have permission to view this message.')
        return redirect('message_list')
    
    # Mark message as read if user is receiver
    if request.user == message.receiver and not message.read:
        message.read = True
        message.save()
    
    return render(request, 'core/messages/detail.html', {'message': message})

@login_required
def delete_message(request, message_id):
    message = get_object_or_404(Message, id=message_id)
    
    # Verify user has permission to delete this message
    if request.user not in [message.sender, message.receiver]:
        messages.error(request, 'You do not have permission to delete this message.')
        return redirect('message_list')
    
    message.delete()
    messages.success(request, 'Message deleted successfully.')
    return redirect('message_list')