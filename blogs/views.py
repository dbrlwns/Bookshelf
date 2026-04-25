from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from blogs.forms import BlogForm
from blogs.models import Blog


def blog_list(request):
    blogs = Blog.objects.all()
    return render(request, "blogs/blog_list.html", {"blogs": blogs})


def blog_detail(request, pk):
    blog = get_object_or_404(Blog, pk=pk)
    return render(request, "blogs/blog_detail.html", {"blog": blog})


@login_required
def blog_add(request):
    if request.method == "POST":
        form = BlogForm(request.POST, request.FILES)
        if form.is_valid():
            blog = form.save(commit=False)
            blog.author = request.user
            blog.save()
            messages.success(request, "Blog created successfully")
            return redirect("blog_list")

        messages.error(request, "Please check the form again")
    else:
        form = BlogForm()

    return render(request, "blogs/blog_add.html", {"form": form})
