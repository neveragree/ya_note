from http import HTTPStatus
from pytils.translit import slugify

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.forms import WARNING
from notes.models import Note

User = get_user_model()


class TestNoteCreation(TestCase):
    TITLE_TEXT = 'Заголовок-1'
    TEXT_TEXT = 'Текст'
    SLUG_TEXT = ''
    EMPTY_WARNING = 'Обязательное поле.'

    @classmethod
    def setUpTestData(cls):
        cls.add_url = reverse('notes:add')
        cls.user = User.objects.create(username='Автор')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.user)
        cls.form_data = {
            'title': cls.TITLE_TEXT,
            'text': cls.TEXT_TEXT,
            'slug': cls.SLUG_TEXT
        }
        cls.empty_form_data = {
            'title': '',
            'text': '',
            'slug': slugify(cls.TITLE_TEXT)
        }

    def test_anonymous_user_cant_create_comment(self):
        self.client.post(self.add_url, data=self.form_data)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)

    def test_user_can_create_comment(self):
        response = self.auth_client.post(self.add_url, data=self.form_data)
        self.assertRedirects(response, '/done/')
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)
        note = Note.objects.get()
        self.assertEqual(note.title, self.TITLE_TEXT)
        self.assertEqual(note.text, self.TEXT_TEXT)
        self.assertEqual(note.slug, 'zagolovok-1')

    def test_user_cant_use_existing_slug(self):
        Note.objects.create(
            title=self.TITLE_TEXT,
            text=self.TEXT_TEXT,
            slug=self.SLUG_TEXT,
            author=self.user
        )
        response = self.auth_client.post(self.add_url, data=self.form_data)
        self.assertFormError(
            response,
            form='form',
            field='slug',
            errors=f'{slugify(self.TITLE_TEXT)}{WARNING}'
        )
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)

    def test_user_cant_send_empty_title_or_text(self):
        response = self.auth_client.post(
            self.add_url,
            data=self.empty_form_data
        )
        self.assertFormError(
            response,
            form='form',
            field='title',
            errors=self.EMPTY_WARNING
        )
        self.assertFormError(
            response,
            form='form',
            field='text',
            errors=self.EMPTY_WARNING
        )
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)


class TestNoteEditDelete(TestCase):
    TITLE_TEXT = 'Заголовок-1'
    TEXT_TEXT = 'Текст'
    SLUG_TEXT = ''
    NEW_TITLE_TEXT = 'Новый заголовок'
    NEW_TEXT_TEXT = 'Новый текст'
    NEW_SLUG_TEXT = 'new-slug'

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader = User.objects.create(username='Читатель')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.notes = Note.objects.create(
            title=cls.TITLE_TEXT,
            text=cls.TEXT_TEXT,
            slug=cls.SLUG_TEXT,
            author=cls.author
        )
        cls.edit_url = reverse('notes:edit', args=(cls.notes.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.notes.slug,))
        cls.done_url = reverse('notes:success')
        cls.form_data = {
            'title': cls.NEW_TITLE_TEXT,
            'text': cls.NEW_TEXT_TEXT,
            'slug': cls.NEW_SLUG_TEXT
        }

    def test_author_can_delete_note(self):
        response = self.author_client.delete(self.delete_url)
        self.assertRedirects(response, self.done_url)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)

    def test_user_cant_delete_note_of_another_user(self):
        response = self.reader_client.delete(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)

    def test_author_can_edit_note(self):
        response = self.author_client.post(self.edit_url, data=self.form_data)
        self.assertRedirects(response, self.done_url)
        self.notes.refresh_from_db()
        self.assertEqual(self.notes.title, self.NEW_TITLE_TEXT)
        self.assertEqual(self.notes.text, self.NEW_TEXT_TEXT)
        self.assertEqual(self.notes.slug, self.NEW_SLUG_TEXT)

    def test_user_cant_edit_note_of_another_user(self):
        response = self.reader_client.post(self.edit_url, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.notes.refresh_from_db()
        self.assertEqual(self.notes.title, self.TITLE_TEXT)
        self.assertEqual(self.notes.text, self.TEXT_TEXT)
        self.assertEqual(self.notes.slug, slugify(self.TITLE_TEXT))
