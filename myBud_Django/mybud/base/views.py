from django.shortcuts import render, redirect
from .models import Room, Topic, Message, User
from .forms import RoomForm, UserForm
from django.db.models import Q
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm




def LoginPage(request):
    page = 'login'
    if request.user.is_authenticated:
        return redirect('home')
    context = {'page' : page}
    if request.method == "POST":
        username = request.POST.get("username").lower()
        password = request.POST.get("password")

        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, "User does not exist")
        user = authenticate(username = username, password = password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Username or Password is incorrect")
    return render(request, "base/login_register.html", context)

def logoutPage(request):
    logout(request)
    return redirect("home")

def registerPage(request):
    form = UserCreationForm()

    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect('home')
        else :
            messages.error(request, "An error occurred during registrations")
    return render(request, "base/login_register.html", {"form": form})

def home(request):
    topics = Topic.objects.all()[0:5]
    q = request.GET.get("q") if request.GET.get("q") != None else ''
    rooms = Room.objects.filter(Q(topic__name__icontains = q) |
                                 Q(name__icontains = q) |
                                 Q(description__icontains = q))
    room_count = rooms.count()

    room_messages = Message.objects.filter(Q(room__topic__name__icontains = q))

    context = {"room": rooms, 'topics':topics, "room_count":room_count, "room_messages": room_messages}
    return render(request, "base/home.html", context)

def room(request, pk):
    room = Room.objects.get(id=pk)
    room_messages = room.message_set.all()
    participants = room.participants.all()

    if request.method == "POST":
        message = Message.objects.create(
            user = request.user,
            room = room,
            body = request.POST.get("body")
        )
        room.participants.add(request.user)
        return redirect('room', pk=room.id)

    context={"room": room, 'room_messages': room_messages, 'participants': participants,  }
    return render(request, "base/room.html", context)


def userProfile(request, pk):
    user = User.objects.get(id=pk)
    room = user.room_set.all()
    room_messages = user.message_set.all()
    topics = Topic.objects.all()
    context = {'user': user, 'room':room, "room_messages":room_messages, "topics":topics, }
    return render(request, "base/profile.html",context)




@login_required(login_url='login')
def createRoom(request):
     page = 'create'
     topics = Topic.objects.all()
     form = RoomForm()
     if request.method == "POST":
        topic_name = request.POST.get("topic")
        topic, created = Topic.objects.get_or_create(name=topic_name)
        Room.objects.create(topic=topic,
                            host = request.user,
                            name = request.POST.get('name'),
                            description = request.POST.get('description'))
        return redirect('home')
        
     context ={'form' : form, 'topics' :topics, 'page': page} 
     return render(request, "base/room_form.html", context)


@login_required(login_url='login')
def updateRoom(request, pk):
    topics = Topic.objects.all()
    room = Room.objects.get(id  = pk)
    form = RoomForm(instance=room)
    if request.method == "POST":
      topic_name = request.POST.get('topic')
      topic, created = Topic.objects.get_or_create(name=topic_name)
      room.name = request.POST.get("name")
      room.description = request.POST.get('description')
      room.topic = topic
      room.save()
      return redirect('home')
    
    context = {'form' : form, 'topics': topics, 'room':room}
    return render(request, "base/room_form.html", context)

@login_required(login_url='login')
def deleteRoom(request, pk):
    room = Room.objects.get(id=pk)
    if request.method == "POST":
        room.delete()
        return redirect("home")
    return render(request, "base/delete.html", {"obj": room})

@login_required(login_url='login')
def deleteMessage(request, pk):
    message = Message.objects.get(id=pk)
    if request.user == message.user:
        if request.method == "POST":
            message.delete()
            return redirect("home")
    return render(request, "base/delete.html", {"obj": message})

@login_required(login_url='login')
def updateUser(request):
    user = request.user
    form = UserForm(instance=user)
    if request.method == 'POST':
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect("user-profile", user.id)
    context = {'form' : form}
    return render(request, "base/update-user.html", context)



def topicsPage(request):
    q = request.GET.get("q") if request.GET.get('q') != None else ""
    topics = Topic.objects.filter(name__icontains=q)
    context ={'topics': topics}
    return render(request, "base/topics.html", context) 


def activityPage(request):
    room_messages = Message.objects.filter()[0:5]
    context = {'room_messages' : room_messages}
    return render(request, "base/activity.html", context)