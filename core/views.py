from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Post, Hero


def home(request):
    return render(request, 'core/home.html')


def contacts(request):
    return render(request, 'core/contacts.html')


class HeroListView(ListView):
    model = Hero
    template_name = 'core/heroes_list.html'
    context_object_name = 'heroes'
    queryset = Hero.objects.filter(is_active=True)


class HeroDetailView(DetailView):
    model = Hero
    template_name = 'core/hero_detail.html'

    def get_queryset(self):
        return Hero.objects.filter(is_active=True)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        lang = self.request.LANGUAGE_CODE
        ctx['description'] = self.object.get_description(lang)
        ctx['services_list'] = [
            s.strip() for s in self.object.services.split(',')
            if s.strip()
        ] if self.object.services else []
        return ctx


def marketplace(request):
    return render(request, 'core/marketplace.html')


class PostListView(ListView):
    model = Post
    template_name = 'core/post_list.html'
    context_object_name = 'posts'
    paginate_by = 10


class PostDetailView(DetailView):
    model = Post
    template_name = 'core/post_detail.html'


class PostCreateView(CreateView):
    model = Post
    fields = ['title', 'body']
    template_name = 'core/post_form.html'
    success_url = reverse_lazy('post_list')


class PostUpdateView(UpdateView):
    model = Post
    fields = ['title', 'body']
    template_name = 'core/post_form.html'
    success_url = reverse_lazy('post_list')


class PostDeleteView(DeleteView):
    model = Post
    template_name = 'core/post_confirm_delete.html'
    success_url = reverse_lazy('post_list')
