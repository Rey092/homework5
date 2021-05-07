import io
from time import time

from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.views.generic.list import ListView
from faker import Faker
from xlsxwriter.workbook import Workbook

from .forms import CommentForm, PostForm, SubscribeForm
from .models import Author, Book, Category, Comment, ContactUs, Post
from .services.authors_service import get_all_authors
from .services.post_service import get_all_posts, get_comments_for_post, get_post, posts_by_author
from .services.subscribe_service import get_all_subscribers, get_author, subscribe
from .tasks import notify_async, send_email_to_all_subscribers


# -----------------------------------------------------------
# view functions for posts - models: Post, Author
# -----------------------------------------------------------


class PostsListView(ListView):
    queryset = get_all_posts()
    template_name = 'pages/post_list.html'


def author_posts(request, author_id):
    return render(request, "pages/post_list.html", {"posts": posts_by_author(author_id)})


def post_create(request):
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("post_list")
    else:
        form = PostForm()

    return render(request, "pages/post_create.html", context={'form': form})


def post_show(request, post_id):
    post = get_post(post_id)
    comments = get_comments_for_post(post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        Comment(content=form.cleaned_data['content'], post_id=post).save()
        return redirect("post_show", post_id)
    else:
        form = CommentForm()
    context = {
        "post": post,
        "form": form,
        "comments": comments
    }
    return render(request, 'pages/post_show.html', context=context)


def post_update(request, post_id):
    post = get_post(post_id)
    err = ""
    if request.method == "POST":
        form = PostForm(instance=post, data=request.POST)
        if form.is_valid():
            form.save()
            return redirect("posts_all")
        else:
            err = "error on update post"
    else:
        form = PostForm(instance=post)
    context = {
        "form": form,
        "err": err,
    }
    return render(request, "pages/post_edit.html", context=context)


# -----------------------------------------------------------
# view functions for authors - models: Author, Subscriber
# -----------------------------------------------------------


def authors_new(request):
    faker = Faker()
    Author(name=faker.name(), email=faker.email()).save()
    return redirect("authors_all")


def authors_all(request):
    context = {
        "authors": Author.objects.all().prefetch_related("books")
    }
    return render(request, "pages/authors.html", context=context)


def author_subscribe(request):
    form = SubscribeForm(request.POST or None)
    # , initial = {'author_id': 1}

    if form.is_valid():
        form.save()

        author = get_author(request)
        email_to = request.POST.get('email_to')

        notify_async.delay(email_to, author.name)
        # notify_async.apply_async(args=(email_to, author.name), countdown=5)

        context = author.serialize()
        return render(request, "pages/subscribe_success.html", context=context)

    return render(request, "pages/subscribe.html", context={"form": form})


def author_subscribers_all(request):
    return render(request, "pages/subscribers.html", {"subscribers": get_all_subscribers()})


# -----------------------------------------------------------
# view functions for Books and Categories - models: Book, Category
# -----------------------------------------------------------


def books_all(request):
    context = {
        "books": Book.objects.all().only("title", "category_id__title").select_related("category_id")
    }
    return render(request, "pages/books.html", context=context)


def categories_all(request):
    context = {
        "categories": Category.objects.all().prefetch_related("books")
    }
    return render(request, "pages/categories.html", context=context)


# -----------------------------------------------------------
# view functions for API - models: Author, Subscriber, Post
# -----------------------------------------------------------


def json_posts(request):
    data = [post.serialize() for post in get_all_posts()]
    return JsonResponse(data, safe=False)


def api_post_show(request, post_id=1):
    data = get_post(post_id).serialize()
    return JsonResponse(data, safe=False)


def api_subscribe(request):
    email_to = request.GET["email_to"]
    author = get_author(request)

    subscribe(author, email_to)
    notify_async(email_to, author.name)

    return HttpResponse(f"You are subscribed on {author}")


def api_subscribers_all(request):
    data = [subscriber.serialize() for subscriber in get_all_subscribers()]
    return JsonResponse(data, safe=False)


def api_authors_all(request):
    data = [author.serialize() for author in get_all_authors()]
    return JsonResponse(data, safe=False)


def api_authors_new(request):
    faker = Faker()
    Author(name=faker.name(), email=faker.email()).save()
    authors = Author.objects.all().values("name", "email")
    return JsonResponse(list(authors), safe=False)


def test(request):
    st = time()
    print('----start')
    send_email_to_all_subscribers.delay()
    time_exec = time() - st
    print(f'----finish. time_exec: {time_exec}')
    return redirect('about_page')


class CreateContactUsView(CreateView):
    success_url = reverse_lazy('home_page')
    model = ContactUs
    template_name = 'pages/contactus_form.html'
    fields = ('email', 'subject', 'message')


def medusweet_xlsx(request):
    output = io.BytesIO()

    workbook = Workbook(output, {'in_memory': True})

    worksheet = workbook.add_worksheet()
    worksheet.set_column('A:A', 30)
    worksheet.set_column('B:B', 100)
    worksheet.write(0, 0, 'Title')
    worksheet.write(0, 1, 'Content')
    worksheet.set_default_row(70)

    cell_format = workbook.add_format()
    cell_format.set_text_wrap()

    queryset = Post.objects.values('title', 'content')
    row = 1
    for obj in queryset.iterator():
        worksheet.write(row, 0, obj['title'], cell_format)
        worksheet.write(row, 1, obj['content'], cell_format)
        row += 1

    workbook.close()
    output.seek(0)

    response = HttpResponse(output.read(), content_type="application/vnd.ms-excel")
    response['Content-Disposition'] = "attachment; filename=medusweet_data.xlsx"

    output.close()

    return response
