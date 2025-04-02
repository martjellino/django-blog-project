from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .tasks import task_do_something
from .models import Post, Category, Tag
from django.contrib import messages
from .forms import PostForm
from .methods import do_something

# Create your views here.
def post_list(request):
    posts = Post.objects.filter(status='published')
    paginator = Paginator(posts, 5)  # 5 posts per page
    page = request.GET.get('page')
    
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page
        posts = paginator.page(1)
    except EmptyPage:
        # If page is out of range, deliver last page of results
        posts = paginator.page(paginator.num_pages)
        
    return render(request, 'blog/post_list.html', {'posts': posts})

def post_detail(request, slug):
    post = get_object_or_404(Post, slug=slug, status='published')
    # List of active comments for this post
    comments = post.comments.filter(active=True)
    
    return render(request, 'blog/post_detail.html', {'post': post, 'comments': comments})

def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug)
    posts = Post.objects.filter(category=category, status='published')
    
    return render(request, 'blog/category_detail.html', {'category': category, 'posts': posts})

def tag_detail(request, slug):
    tag = get_object_or_404(Tag, slug=slug)
    posts = Post.objects.filter(tags__in=[tag], status='published')
    
    return render(request, 'blog/tag_detail.html', {'tag': tag, 'posts': posts})

@login_required
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            # do_something()
            task_do_something() ## run in the background
            
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            # For many-to-many relationships, save them after initial save
            form.save_m2m()  # This saves the tags
            messages.success(request, 'Your post has been created!')
            return redirect('post_detail', slug=post.slug)
    else:
        form = PostForm()
    
    return render(request, 'blog/post_form.html', {'form': form, 'title': 'Create Post'})