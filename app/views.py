from django.core.files.base import File
from app.models import GeneralAdmin, Group, UploadInvite, UserProfile, Stories, Idea, Tech, User
from app.forms import CohortForm, InviteUsers, SignupForm, UserProfileForm,IdeaCreationForm,CreateStoryForm, DiscussionForm, FundraiserForm, TechNewsForm
from app.models import GeneralAdmin, Group, UserProfile, Stories, Idea, Tech, User
from app.forms import CohortForm, SignupForm, UserProfileForm,IdeaCreationForm,CreateStoryForm, DiscussionForm, FundraiserForm, TechNewsForm
from django.shortcuts import render, redirect
from django.shortcuts import render,redirect
from django.urls import reverse
import stripe
from django.shortcuts import render, get_object_or_404,redirect
from django.contrib.auth import login, authenticate
from django.contrib import messages
import datetime as dt
from django.http import HttpResponseRedirect
from django.contrib.sites.shortcuts import get_current_site
from .email import collaborate_new, send_invite
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from .utils import generate_token
from django.utils.encoding import force_bytes, force_text
from django.views import View
import mimetypes
import os
from django.http.response import HttpResponse
import pandas as pd
from csv import DictReader
import random


import threading

from django.http import HttpResponseRedirect,request,JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from app.forms import (CohortForm, CreateStoryForm, IdeaCreationForm,
                       SignupForm, TechNewsForm, UserProfileForm)
from app.models import Group, Idea, Stories, Tech, UserProfile

from .forms import (CohortForm, CreateStoryForm, DiscussionForm,
                    FundraiserForm, IdeaCreationForm, SignupForm, TechNewsForm,
                    UserProfileForm,Add_userForm)
from .models import Group, Idea, Stories, Tech, UserProfile

# Create your views here.

stripe.api_key = "YOUR SECRET KEY"

def index(request):
    groups = Group.objects.all()
    stories = Stories.objects.order_by("-id")
    #tech = TechNews.objects.all()
    return render(request,'index.html', {'groups':groups,'stories':stories})
    
def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('index')
    else:
        form = SignupForm()
    return render(request, 'registration/registration_form.html', {'form': form})

   
def profile(request):
    if request.method == 'POST':
        profile_form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if  profile_form.is_valid():
            profile_form.save()
            return redirect('index')
    else:
        profile_form = UserProfileForm(instance=request.user)
        context = { 
            "profile_form": profile_form
            }
    return render(request, 'user_profile.html',context)

def cohort(request):
    title = "Cohorts"
    if request.method == 'POST':
        
        form = CohortForm(request.POST, request.FILES)
        if form.is_valid():
            group = form.save(commit=False)
            group.creator = request.user
            group.date_created = dt.datetime.now()
            group.save()
            group.members.add(UserProfile.objects.get(user=request.user))
            group.members.add(request.POST.get('admin'))
            group.save()
            messages.success(request, 'A new Cohort has been created')
            return redirect('index')
        else:
            messages.warning(request, 'Invalid form')
            return render(request, 'cohort.html', {'title':title,'form': form})
    else:
        form = CohortForm()
    return render(request, 'cohort.html', {'title':title,'form': form})

# Create your views here.

#-----------------------------------------------------------------------------------------
#view function that renders to meet_collegues template
def meet_collegues(request):
  '''
  renders meet_collegues template
  '''
  form = IdeaCreationForm
  try:
    ideas = Idea.objects.all()
  except Idea.DoesNotExist:
    ideas = None
  if request.method == 'POST':
    form = IdeaCreationForm(request.POST, request.FILES)
    if form.is_valid():
      new_idea = form.save(commit=False)
      new_idea.date_created = dt.datetime.now()
      new_idea.owner = UserProfile.objects.get(id = 1)#change filter to user = request.user
      new_idea.save()

      try:
        ideas = Idea.objects.all()
      except Idea.DoesNotExist:
        ideas = None

      context = {
        'form':form,
        'ideas':ideas
        }
      return render(request, 'meetcollegues.html', context)

    else:
      messages.warning(request, 'Invalid Form')
      return redirect('meet_collegues')

  context = {
    'form':form,
    'ideas':ideas

  }
  return render(request, 'meetcollegues.html', context)

#view function that renders to single idea page
def single_idea(request, id):
  '''
  Renders a found idea object
  '''
  idea = Idea.objects.get(id = id)
  if idea.collaborators.id == request.user.id:
      messages.success(request, 'You are already a collaborator to this project')
  else:  
    if request.method == 'POST':
        skills = request.POST.get('skills')
        new_join = request.user
        idea.collaborators.add(1) #use user profile query UserProfile.objects.filter(user = new_join).last()

        #send email of a user joining a team
        collaborate_new(new_join, idea, idea.owner.user.email, skills)
    context = {
        'idea':idea
    }

    messages.success(request, 'You are Now a collaborator. The Owner has been Notified')  
    return redirect('meet_collegues')

stripe.api_key = "YOUR SECRET KEY"


def index(request):
    stories = Stories.objects.order_by("-id")
    # technews = TechNews.objects.order_by("-id")
    return render(request,"index.html",{"stories":stories})
    
def create_story(request):
    form = CreateStoryForm()
    if request.method == 'POST':
        form = CreateStoryForm(request.POST or None,request.FILES)
        if form.is_valid():
            story = form.save(commit=False)
            story.creator = request.user
            story.save()
        return HttpResponseRedirect(request.path_info)

    else:
        form = CreateStoryForm()
    return render(request,"storyform.html",{"form":form})
    return render(request, 'index.html')


def TechNews(request):
    form = TechNewsForm()
    if request.method == 'POST':
        form = TechNewsForm(request.POST or None,request.FILES)
        if form.is_valid():
            news = form.save(commit=False)
            news.creator = request.user
            news.save()
        return HttpResponseRedirect(request.path_info)
    else:
        form = TechNewsForm()
    return render(request,'newsform.html',{"form":form})

# Start a discussion.
def Discussion(request):
    current_user = request.user
    if request.method == 'POST':
        form = DiscussionForm(request.POST, request.FILES)
        if form.is_valid():
            discussion = form.save(commit=False)
            discussion.user = current_user
            
          
            
def charge(request):
    
    if request.method == 'POST':
         print('Data:', request.POST)

    amount = int(request.POST['amount']) 

    customer = stripe.Customer.create(
            email=request.POST['email'],
            name=request.POST['nickname'],
            source=request.POST['stripeToken']
            )

    charge = stripe.Charge.create(
            customer=customer,
            amount=amount*100,
            currency='usd',
            description="Donation"
            )

    return redirect(reverse('success', args=[amount]))


def successMsg(request, args):
    amount = args
    return render(request, 'success.html', {'amount':amount})

    form = DiscussionForm()
    return render(request, 'new_discussion.html', {"form": form})
    
def Fundraiser(request):
    title = 'Start A Fundraiser'
    current_user = request.user
    if request.method == 'POST':
        form = FundraiserForm(request.POST, request.FILES)
        if form.is_valid():
            fundraise = form.save(commit=False)
            fundraise.creator = current_user
            fundraise.date_created = dt.datetime.now()
            fundraise.save()


    else:
        form = FundraiserForm()
    return render(request, 'new_fundraiser.html', {'title':title,"form": form})
#views to summary on the admin dashboard
def summary(request):
    '''
    renders summary on admin dashboard
    '''
    title = 'Admin - Summary'
    
    users = UserProfile.get_users()
    active_users = User.objects.filter(is_active = True)
    inactive_users = User.objects.filter(is_active = False)

    projects = Idea.get_open_projects()
    closed_projects = Idea.get_closed_projects()
    groups = Group.get_groups()
    admins = GeneralAdmin.get_admins()[:5]
    articles = Stories.get_stories()


    def close_project():
        project_id = request.POST.get('close_proj')
        project = Idea.objects.filter(id = project_id)
        if project:
            project.update(is_open = False)
    
    if request.method == 'POST':
        close_project()

        return redirect('admin_dashboard')


    context = {
        'inactive_users':inactive_users,
        'closed_projects':closed_projects,
        'articles':articles,
        'admins':admins,
        'users':users,
        'projects':projects,
        'groups':groups,
        'title':title
    }

    return render(request, 'admin_dash/dashboard.html', context)

#view function that renders to invite members page
def invite_members(request):
    '''
    renders invite member form
    invites single users
    invotes multiple users
    '''
    def invite_new_user(f_name, l_name, email):

        rando = random.randint(0, 1000)
        new_user = User(username = f_name+l_name+str(rando), first_name = f_name, last_name = l_name, email = email, is_active = False)
        new_user.save()
        current_site = get_current_site(request)
        domain = current_site.domain
        uid = urlsafe_base64_encode(force_bytes(new_user.pk))
        token = generate_token.make_token(new_user)
        
        send_invite(email, domain , uid, token)

        messages.success(request, f'Congratulations! You have succesfully Added a new User!')
        return redirect('invite_members')
    title = 'Invite Members'
    if 'single_invite' in request.POST and request.method == "POST":
        f_name = request.POST.get('first_name')
        l_name = request.POST.get('last_name')
        email = request.POST.get('user_email')

        #call the function that sends email to new users
        invite_new_user(f_name, l_name, email)
    form = InviteUsers

    if 'multiple_invite' in request.POST and request.method == 'POST':
        form = InviteUsers(request.POST, request.FILES)
        if form.is_valid:
            form.save()

            form_to_read = UploadInvite.objects.all().last()

            with open((form_to_read.file_path).path, 'r') as read_obj:
                csv_dict_reader = DictReader(read_obj)
                for row in csv_dict_reader:
                    f_name = row['first_name']
                    l_name = row['last_name']
                    email = row['email']

                    invite_new_user(f_name, l_name, email)
       
    context = {
        'form':form,
        'title':title,
    }

    return render(request, 'invite_member.html', context)

class InviteUserView(View):
    '''
    View function that generates a new token for each new user based on their uid
    '''
    def get(self, request, uidb64, token):
        try:
            uid = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except Exception as identifier:
            user = None
        if user is not None and generate_token.check_token(user, token):
            user.is_active = True
            user.save()
            messages.add_message(request, messages.SUCCESS,
                                 'user is invited successfully')
            return redirect('user_profile.html')
        return render(request, 'user_profile.html')
#--------------------------------------------------------------------------------------------
#function enabling dowloading of user csv file
def download_csv(request):
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    filename = 'Invite_users.csv'

    filepath = BASE_DIR + '/app/Files/' + filename
    path = open(filepath, 'r')
    mime_type = mimetypes.guess_type(filepath)
    response = HttpResponse(path, content_type = mime_type)
    response['Content-Disposition'] = "attachment; filename=%s" % filename

    return response

    
    return render(request, 'admin_dash/dashboard.html', context)

def create_user(request):
    '''
    View function to add a new students members into the alumni platform and send them an invitation email
    '''
    if request.method == 'POST':
        form = Add_userForm(request.POST)
        email = request.POST.get('email')
        if form.is_valid():
            user = form.save(commit = False)
            user.is_active = False
            user.save()
            current_site = get_current_site(request)
            email_subject = 'Invitation to Alumni Community'
            message = render_to_string('invitation.html',
                                    {
                                        'user': user,
                                        'domain': current_site.domain,
                                        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                                        'token': generate_token.make_token(user)
                                    }
                                    )
            email_message = EmailMessage(
                email_subject,
                message,
                settings.EMAIL_HOST_USER,
                [email]
            )
            EmailThread(email_message).start()
            messages.add_message(request, messages.SUCCESS,
                                'invaitation sent  succesfully')
            return redirect('registration')

            messages.success(request, f'Congratulations! You have succesfully Added a new User!')
            return redirect('/user_list/')
    else:
        form = Add_userForm()
    return render(request, 'create_user.html', {"form": form})


class InviteUserView(View):
    '''
    View function that generates a new token for each new user based on their uid
    '''
    def get(self, request, uidb64, token):
        try:
            uid = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except Exception as identifier:
            user = None
        if user is not None and generate_token.check_token(user, token):
            user.is_active = True
            user.save()
            messages.add_message(request, messages.SUCCESS,
                                 'user is invited successfully')
            return redirect('')
        return render(request, '')

class EmailThread(threading.Thread):

    def __init__(self, email_message):
        self.email_message = email_message
        threading.Thread.__init__(self)

    def run(self):
        self.email_message.send()

def Fundraiser(request):
    
    return render(request,'new_fundraiser.html')

