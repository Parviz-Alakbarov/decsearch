from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from .models import Profile
from .forms import CustomUserCreationForm, ProfileForm, SkillForm


def profiles(request):
    profiles = Profile.objects.all()
    return render(request, 'users/profiles.html', {'profiles': profiles})


def userProfile(request, pk):
    profile = Profile.objects.get(id=pk)
    skills = profile.skill_set.exclude(description__exact="")
    otherSkills = profile.skill_set.filter(description="")
    projects = profile.porject_set.all()
    return render(request, 'users/user-profile.html',
                  {'profile': profile, 'skills': skills, 'otherSkills': otherSkills, 'projects': projects})


def loginPage(request):
    if request.user.is_authenticated:
        return redirect('profiles')

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, 'UserName does not exist')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('profiles')
        else:
            messages.error(request, 'Username or Password is incorrect')

    return render(request, 'users/login_register.html', {'page': 'login'})


def logoutUser(request):
    logout(request)
    messages.info(request, "User has been logouted")
    return redirect('login')


def registerUser(request):
    if request.user.is_authenticated:
        return redirect('profiles')
    form = CustomUserCreationForm()

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            messages.success(request, 'User have been created successfully')
            login(request, user)
            return redirect('edit-account')
        else:
            messages.error(request, 'An error has occurred during registration')
    return render(request, 'users/login_register.html', {'page': 'register', 'form': form})


@login_required(login_url='login')
def userAccount(request):
    profile = request.user.profile
    skills = profile.skill_set.all()
    projects = profile.porject_set.all()
    print(projects)
    return render(request, 'users/account.html', {'profile': profile, 'skills': skills, 'projects': projects})


@login_required(login_url='login')
def editAccount(request):
    profile = request.user.profile
    form = ProfileForm(instance=profile)
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('account')
    return render(request, 'users/profile_form.html', {'form': form})


@login_required(login_url='login')
def createSkill(request):
    form = SkillForm()
    if request.method == 'POST':
        form = SkillForm(request.POST)
        if form.is_valid():
            skill = form.save(commit=False)
            skill.owner = request.user.profile
            skill.save()
            messages.success(request, 'Skill created :)')
            return redirect('account')
    return render(request, 'users/skill_form.html', {'form': form})


@login_required(login_url='login')
def updateSkill(request, pk):
    profile = request.user.profile
    try:
        skill = profile.skill_set.get(id=pk)
    except:
        messages.error(request, 'Skill not found!!!')
        return redirect('account')
    form = SkillForm(instance=skill)
    if request.method == 'POST':
        form = SkillForm(request.POST, instance=skill)
        if form.is_valid():
            form.save()
            messages.success(request, 'Skill added :)')
            return redirect('account')
    return render(request, 'users/skill_form.html', {'form': form})


@login_required(login_url='login')
def deleteSkill(request, pk):
    profile = request.user.profile
    try:
        skill = profile.skill_set.get(id=pk)
    except:
        messages.error(request, 'Skill not found!!!')
        return redirect('account')

    if request.method == 'POST':
        skill.delete()
        messages.success(request, 'Skill Deleted!')
        return redirect('account')
    return render(request, 'delete_template.html', {'object': skill})