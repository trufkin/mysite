from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from core.models import Post

User = get_user_model()


# ── Model ──────────────────────────────────────────────────────────────────────

class CoreModelTests(TestCase):
    def test_create_post(self):
        Post.objects.create(title='T1', body='B1')
        self.assertEqual(Post.objects.count(), 1)

    def test_str_representation(self):
        p = Post(title='Hello')
        self.assertEqual(str(p), 'Hello')


# ── Web views ──────────────────────────────────────────────────────────────────

class CoreViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.post = Post.objects.create(title='Test Post', body='Body text')

    def test_index_view(self):
        resp = self.client.get('/')
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Welcome to Core App')

    def test_post_list_view(self):
        resp = self.client.get(reverse('post_list'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Test Post')

    def test_post_detail_view(self):
        resp = self.client.get(reverse('post_detail', args=[self.post.pk]))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Test Post')

    def test_post_create_view_get(self):
        resp = self.client.get(reverse('post_create'))
        self.assertEqual(resp.status_code, 200)

    def test_post_create_view_post(self):
        resp = self.client.post(reverse('post_create'), {'title': 'New', 'body': 'Body'})
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(Post.objects.filter(title='New').exists())

    def test_post_update_view(self):
        resp = self.client.post(
            reverse('post_edit', args=[self.post.pk]),
            {'title': 'Updated', 'body': 'New body'},
        )
        self.assertEqual(resp.status_code, 302)
        self.post.refresh_from_db()
        self.assertEqual(self.post.title, 'Updated')

    def test_post_delete_view(self):
        resp = self.client.post(reverse('post_delete', args=[self.post.pk]))
        self.assertEqual(resp.status_code, 302)
        self.assertFalse(Post.objects.filter(pk=self.post.pk).exists())


# ── REST API ───────────────────────────────────────────────────────────────────

class PostAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='tester', password='pass1234')
        self.token = Token.objects.create(user=self.user)
        self.post = Post.objects.create(title='API Post', body='API Body')

    def _auth(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')

    # Unauthenticated reads
    def test_list_posts_unauthenticated(self):
        resp = self.client.get('/api/posts/')
        self.assertEqual(resp.status_code, 200)

    def test_retrieve_post_unauthenticated(self):
        resp = self.client.get(f'/api/posts/{self.post.pk}/')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['title'], 'API Post')

    # Unauthenticated writes should be rejected (403 with SessionAuthentication)
    def test_create_post_unauthenticated(self):
        resp = self.client.post('/api/posts/', {'title': 'X', 'body': 'Y'})
        self.assertIn(resp.status_code, [401, 403])

    # Authenticated CRUD
    def test_create_post_authenticated(self):
        self._auth()
        resp = self.client.post('/api/posts/', {'title': 'New API', 'body': 'Body'})
        self.assertEqual(resp.status_code, 201)
        self.assertTrue(Post.objects.filter(title='New API').exists())

    def test_update_post_authenticated(self):
        self._auth()
        resp = self.client.patch(f'/api/posts/{self.post.pk}/', {'title': 'Updated API'})
        self.assertEqual(resp.status_code, 200)
        self.post.refresh_from_db()
        self.assertEqual(self.post.title, 'Updated API')

    def test_delete_post_authenticated(self):
        self._auth()
        resp = self.client.delete(f'/api/posts/{self.post.pk}/')
        self.assertEqual(resp.status_code, 204)
        self.assertFalse(Post.objects.filter(pk=self.post.pk).exists())

    # Filtering / search
    def test_search_posts(self):
        Post.objects.create(title='Unique title xyz', body='b')
        resp = self.client.get('/api/posts/?search=xyz')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['count'], 1)

    def test_ordering_posts(self):
        Post.objects.create(title='A Post', body='b')
        resp = self.client.get('/api/posts/?ordering=title')
        self.assertEqual(resp.status_code, 200)
        titles = [p['title'] for p in resp.data['results']]
        self.assertEqual(titles, sorted(titles))

    # Pagination
    def test_pagination_present(self):
        resp = self.client.get('/api/posts/')
        self.assertIn('count', resp.data)
        self.assertIn('results', resp.data)
