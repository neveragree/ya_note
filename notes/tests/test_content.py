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


class TestNotesContent(TestCase):
    NOTES_URL = reverse('notes:list')

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.reader = User.objects.create(username='Читатель')
        cls.notes = Note.objects.create(
            title='Заметка',
            text='Текст заметки',
            slug='slug',
            author=cls.author,
        )

    def test_note_in_object_list(self):
        users_results = (
            (self.author, True),
            (self.reader, False)
        )
        for user, result in users_results:
            self.client.force_login(user)
            response = self.client.get(self.NOTES_URL)
            object_list = response.context['object_list']
            notes_count = len(object_list)
            self.assertEqual(notes_count, result)


class TestNotesForm(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.notes = Note.objects.create(
            title='Заметка',
            text='Текст заметки',
            slug='slug',
            author=cls.author,
        )
        cls.urls = (
            ('notes:add', None),
            ('notes:edit', (cls.notes.slug,))
        )

    def test_pages_contains_form(self):
        self.client.force_login(self.author)
        for name, args in self.urls:
            url = reverse(name, args=args)
            response = self.client.get(url)
            self.assertIn('form', response.context)
