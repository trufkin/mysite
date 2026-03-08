from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, get_user_model
from django.contrib.auth.mixins import UserPassesTestMixin
from django.core import signing
from django.core.mail import send_mail
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from .forms import SignUpForm
from .models import Post, Hero, UserProfile

EMAIL_CONFIRM_SALT = 'bolohan-email-confirm'
EMAIL_CONFIRM_MAX_AGE = 3 * 24 * 3600  # 3 days in seconds


def home(request):
    return render(request, 'core/home.html')


def contacts(request):
    return render(request, 'core/contacts.html')


# ── Email-confirmation helpers ─────────────────────────────────────────────────

class EmailConfirmedMixin(UserPassesTestMixin):
    """CBV mixin: require an authenticated user with a confirmed email address."""
    def test_func(self):
        u = self.request.user
        return (
            u.is_authenticated
            and hasattr(u, 'profile')
            and u.profile.email_confirmed
        )

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            messages.warning(
                self.request,
                'Please confirm your email address before creating listings.',
            )
            return redirect('marketplace')
        return super().handle_no_permission()


# ── Sign-up ────────────────────────────────────────────────────────────────────

class SignUpView(CreateView):
    form_class = SignUpForm
    template_name = 'registration/signup.html'

    def form_valid(self, form):
        user = form.save()
        token = signing.dumps(user.pk, salt=EMAIL_CONFIRM_SALT)
        confirm_url = self.request.build_absolute_uri(
            reverse('confirm_email', args=[token])
        )
        body = render_to_string('registration/email_body.txt', {
            'username': user.username,
            'confirmation_url': confirm_url,
        })
        send_mail(
            subject='Confirm your Bolohan account',
            message=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=True,
        )
        return HttpResponseRedirect(
            reverse('confirm_email_sent') + f'?email={user.email}'
        )


def confirm_email_sent(request):
    email = request.GET.get('email', '')
    return render(request, 'registration/confirm_email_sent.html', {'email': email})


def confirm_email(request, token):
    User = get_user_model()
    try:
        uid = signing.loads(token, salt=EMAIL_CONFIRM_SALT, max_age=EMAIL_CONFIRM_MAX_AGE)
        user = User.objects.get(pk=uid)
    except (signing.BadSignature, signing.SignatureExpired, User.DoesNotExist):
        return render(request, 'registration/confirm_email.html', {'valid': False})

    profile, _ = UserProfile.objects.get_or_create(user=user)
    if not profile.email_confirmed:
        profile.email_confirmed = True
        profile.save()

    login(request, user)
    return render(request, 'registration/confirm_email.html', {'valid': True})


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
    u = request.user
    email_confirmed = (
        u.is_authenticated
        and hasattr(u, 'profile')
        and u.profile.email_confirmed
    )
    return render(request, 'core/marketplace.html', {'email_confirmed': email_confirmed})


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
