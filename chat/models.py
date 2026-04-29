from django.db import models


class Room(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True) # url에 쓰일 값  활용) /chat/chat-room/
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Message(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='messages')
    # author = models.CharField(max_length=50)  # 익명 닉네임
    author = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="chat_messages")
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f'[{self.room.name}] {self.author}: {self.content[:30]}'


"""
1. 초기 chat 앱 생성 시 익명 채팅기능으로 Message class에 author을 CharField로 설정한걸
    ForeignKey로 변경
    -> 템플릿에서 message.author == user.username를 message.author == user로 변경
    -> consumers.py에서 user = self.scope['user']로 사용자 받아 
        profile_image_url = await self.save_message(user, message)로 이미지 메시지에 전송
    -> consumers.py에서 메시지 저장과 메시지 전송에도 이미지 url 삽입
    -> JS에서 appendMessage() 함수에 프로필 이미지도 받도록 추가
        avatarHtml에 프로필 이미지url 추가
"""