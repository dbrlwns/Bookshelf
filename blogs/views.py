import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.http.response import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from blogs.forms import BlogForm
from blogs.models import Blog, Comment, Tag


def blog_list(request):
    blogs = Blog.objects.all()
    tags = Tag.objects.all()

    # tag를 Query로 받을 시 필터
    selected_tag_slug = (request.GET.get("tag") or "").strip()
    selected_tag = None
    if selected_tag_slug:
        selected_tag = get_object_or_404(Tag, slug=selected_tag_slug)
        blogs = blogs.filter(tags=selected_tag)

    context = {
        "blogs": blogs,
        "tags": tags,
        "selected_tag": selected_tag,
    }
    return render(request, "blogs/blog_list.html", context)


def blog_detail(request, pk):
    blog = get_object_or_404(Blog, pk=pk)
    return render(request, "blogs/blog_detail.html", {"blog": blog})


@login_required
@require_POST
def blog_delete(request, pk):
    blog = get_object_or_404(Blog, pk=pk)

    if blog.author != request.user:
        return HttpResponseForbidden("본인이 작성한 글만 삭제할 수 있습니다.")

    blog.delete()
    messages.success(request, "Blog deleted successfully")
    return redirect("blog_list")


@require_POST
def comment_add(request, pk):
    blog = get_object_or_404(Blog, pk=pk)

    if not request.user.is_authenticated: # 비로그인 접근시
        return JsonResponse(
            {"ok": False, "error": "로그인 후 댓글을 작성할 수 있습니다."},
            status=401,
        )

    try:
        payload = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"ok": False, "error": "Invalid JSON payload"}, status=400)

    content = (payload.get("content") or "").strip()

    if not content:
        return JsonResponse({"ok": False, "error": "댓글 내용을 입력해주세요."}, status=400)


    comment = Comment.objects.create(
        blog=blog,
        author=request.user,
        content=content,
    )

    return JsonResponse(
        {
            "ok": True,
            "comment": {
                "id": comment.id,
                "blog_id": blog.id,
                "author": comment.author.username,
                "content": comment.content,
                "created_at": comment.created_at.strftime("%Y-%m-%d %H:%M"),
            },
        },
        status=201,
    )


@login_required
def blog_add(request):
    if request.method == "POST":
        form = BlogForm(request.POST, request.FILES)
        if form.is_valid():
            blog = form.save(commit=False)
            blog.author = request.user
            blog.save()

            # 태그 추가
            tags = []
            for name in form.cleaned_data["tag_names"]:
                tag, created = Tag.objects.get_or_create(name=name)
                tags.append(tag)
            blog.tags.set(tags) # 이건 처음 써보네
            messages.success(request, "Blog created successfully")
            return redirect("blog_list")

        messages.error(request, "Please check the form again")
    else:
        form = BlogForm()

    return render(request, "blogs/blog_add.html", {"form": form})


@login_required
def blog_edit(request, pk):
    blog = get_object_or_404(Blog, pk=pk)

    if blog.author != request.user:
        return HttpResponseForbidden("본인이 작성한 글만 수정할 수 있습니다.")

    if request.method == "POST":
        form = BlogForm(request.POST, request.FILES, instance=blog)
        if form.is_valid():
            form.save()

            # 태그 추가
            tags = []
            for name in form.cleaned_data["tag_names"]:
                tag, created = Tag.objects.get_or_create(name=name)
                tags.append(tag)
            blog.tags.set(tags)

            messages.success(request, "Blog updated successfully")
            return redirect("blog_detail", pk=blog.pk)

        messages.error(request, "Please check the form again")
    else:
        initial = {
            "tag_names": ", ".join(tag.name for tag in blog.tags.all())
        }
        form = BlogForm(instance=blog, initial=initial)

    context = {
        "form": form,
        "is_edit": True,
        "blog": blog,
    }
    return render(request, "blogs/blog_add.html", context)


"""
1. blog.tags.set(tags) : blog 모델에 ManyToManyField로 tags가 있음.
    이 블로그에 연결된 태그 목록을 전달받은 tags 통으로 교체함.
    ManyToManyField는 blog가 DB에 저장된 뒤에 연결할 수 있음.(blog.id가 필요해서)
    
2. initial 파라미터 : instance는 모델 필드의 기존 값을 채워줌.
    하지만 tag_names는 Blog 모델에 있는 필드가 아님. (form에서 추가한 필드)
    initial = { "tag_names": "파이썬, 장고, AI" } 이렇게 넣어주면 내용이 채워짐


"""