from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.text import slugify

from .models import Room


def index(request):
    rooms = Room.objects.all()
    context = {
        "rooms": rooms,
        "open_create_modal": False,
        "room_name_value": "",
    }

    if request.method == "POST":
        room_name = (request.POST.get("room_name") or "").strip()
        context["room_name_value"] = room_name

        if not room_name:
            messages.error(request, "채팅방 이름을 입력해주세요.")
            context["open_create_modal"] = True
            return render(request, "chat/chat_list.html", context)

        base_slug = slugify(room_name) or "chat-room"
        slug = base_slug
        counter = 1
        while Room.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1

        room = Room.objects.create(name=room_name, slug=slug)
        messages.success(request, "채팅방이 생성되었습니다.")
        return redirect("chat_room", room_slug=room.slug)

    return render(request, 'chat/chat_list.html', context)


def room(request, room_slug):
    room = get_object_or_404(Room, slug=room_slug)
    chat_messages = room.messages.all()
    return render(request, 'chat/room.html', {'room': room, 'chat_messages': chat_messages})
