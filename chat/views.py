from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
# from django.contrib.auth.models import User
from authentication.models import CustomUser
from .models import Room
from zoneinfo import ZoneInfo
# from .schedulers import resend_notification

# Create your views here.


@login_required
def index(request):
    if request.user.is_authenticated:
        group = Room.objects.filter(is_group=True,
                                    members=request.user)
        unconnected_user = []
        private = Room.objects.filter(is_group=False,
                                    members=request.user)
        connected_user = []
        for mem in private:
            user = mem.members.exclude(id=request.user.id).first()
            if user:
                connected_user.append(user)

            # print("-----",other_user)
        print("--------", connected_user)
        connected_user_ids = [user.id for user in connected_user]
        unconnected_user = CustomUser.objects.exclude(
            id__in=connected_user_ids).exclude(id=request.user.id)
        print('u--------', unconnected_user)
        context = {
            'rooms': group,
            'unconnected_user': unconnected_user,
            'connected_user': connected_user,
        }
        # for scheduling notification for unseen notification
        # resend_notification(request.user.id)
        return render(request, 'chat/index.html', context)    


@login_required
def create_room(request):
    if request.method == 'POST':
        room_name = request.POST.get('room_name')
        user = request.user
        # print(user)
        room = Room.objects.filter(room_name=room_name)
        if room.exists():
            messages.error(request, 'Room already exists')
            return redirect('chat:create-room')
        else:
            room = Room.objects.create(
                room_name=room_name,
                is_group=True,
                admin=user,
            )
            room.members.add(user)
            room.save()
            messages.success(request, 'Room created successfully')
            return redirect('chat:room', room_name=room_name)
    return render(request, 'chat/create_room.html')


@login_required
def private_room(request, username):
    user1 = request.user
    user2 = get_object_or_404(CustomUser, username=username)  # safe

    # deterministic room name
    room_name = "private_"+"_".join(sorted([str(user1.id), str(user2.id)]))

    # get or create the private room
    room, created = Room.objects.get_or_create(
        room_name=room_name,
        defaults={'is_group': False}
    )

    # add members if newly created
    if created:
        room.members.add(user1, user2)
        room.save()
        messages.success(request, 'Private room created successfully')

    return redirect('chat:room', room_name=room_name)


@login_required
def room(request, room_name):
    room = get_object_or_404(Room, room_name=room_name)
    message_history = room.messages.select_related('sender').all()
    message_history_context = [
        {
            "sender": msg.sender.username,
            "content": msg.content,
            "timestamp": msg.timestamp.astimezone(ZoneInfo("Asia/Kathmandu")).strftime("%H:%M")
        }
        for msg in message_history
    ]
    is_admin = False
    if room.admin == request.user:
        is_admin = True

    # print(message_history_context)
    if room.is_group:
        return render(request, 'chat/room.html', {'room_name': room_name, 'chat_history': message_history_context, 'is_admin': is_admin})
    else:
        if room.members.contains(request.user):
            return render(request, 'chat/room.html', {'room_name': room_name, 'chat_history': message_history_context})
        return HttpResponse('Not accessed')


@login_required
def add_members(request, room_name):
    room = get_object_or_404(Room, room_name=room_name)
    users = CustomUser.objects.exclude(
        id__in=[x.id for x in room.members.all()])

    if request.user == room.admin:
        if request.method == 'POST':
            selected_user = request.POST.getlist('users')
            print(selected_user)
            users_to_add = CustomUser.objects.filter(id__in=selected_user)
            print(users_to_add)
            room.members.add(*users_to_add)
            return redirect('chat:room', room_name=room_name)
    else:
        return HttpResponse('Page not found')

    return render(request, 'chat/add-members.html', {'room_name': room_name, 'users': users})
