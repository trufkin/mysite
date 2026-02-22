from django.test import TestCase, Client
from core.models import Post


class CoreModelTests(TestCase):
	def test_create_post(self):
		Post.objects.create(title='T1', body='B1')
		self.assertEqual(Post.objects.count(), 1)


class CoreViewTests(TestCase):
	def setUp(self):
		self.client = Client()

	def test_index_view(self):
		resp = self.client.get('/')
		self.assertEqual(resp.status_code, 200)
		self.assertContains(resp, 'Welcome to Core App')
