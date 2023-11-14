from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestNotesOrder(TestCase):
    NOTES_URL = reverse('notes:list')

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        for index in range(2):
            notes = Note.objects.create(
                title=f'Заметка {index}',
                text='Текст заметки',
                slug=f'slug-{index}',
                author=cls.author,
            )
            notes.save()

    def test_notes_order(self):
        self.client.force_login(self.author)
        response = self.client.get(self.NOTES_URL)
        object_list = response.context['object_list']
        all_pks = [notes.pk for notes in object_list]
        sorted_pks = sorted(all_pks)
        self.assertEqual(all_pks, sorted_pks)


class TestNotesForm(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.add_url = reverse('notes:add')

    def test_authorized_client_has_form(self):
        self.client.force_login(self.author)
        response = self.client.get(self.add_url)
        self.assertIn('form', response.context)
