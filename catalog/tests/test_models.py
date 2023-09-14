
from django.test import TestCase
from django.db import models

from catalog.models import Author, Book, BookInstance, Genre, Language

# Tests related to the model named Author
class AuthorModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by all test methods (run only once)
        Author.objects.create(first_name='Big', last_name='Bob')

    def test_first_name_label(self):
        author = Author.objects.get(id=1)
        field_label = author._meta.get_field('first_name').verbose_name
        self.assertEqual(field_label, 'first name')

    def test_first_name_max_length(self):
        author = Author.objects.get(id=1)
        max_length = author._meta.get_field('first_name').max_length
        self.assertEqual(max_length, 100)

    def test_last_name_label(self):
        author = Author.objects.get(id=1)
        last_name_expected_label = 'last name'
        last_name_actual_label = author._meta.get_field('last_name').verbose_name
        self.assertEqual(last_name_actual_label, last_name_expected_label)

    def test_last_name_max_length(self):
        author = Author.objects.get(id=1)
        last_name_expected_max_length = 100
        last_name_actual_max_length = author._meta.get_field('last_name').max_length
        self.assertEqual(last_name_actual_max_length, last_name_expected_max_length)

    def test_date_of_birth_label(self):
        author = Author.objects.get(id = 1)
        date_of_birth_expected_label = 'date of birth'
        date_of_birth_actual_label = author._meta.get_field('date_of_birth').verbose_name
        self.assertEqual(date_of_birth_actual_label, date_of_birth_expected_label)

    def test_date_of_death_label(self):
        author = Author.objects.get(id=1)
        field_label = author._meta.get_field('date_of_death').verbose_name
        self.assertEqual(field_label, 'Died on')
    
    def test_object_name_is_last_name_comma_first_name(self):
        author = Author.objects.get(id=1)
        expected_object_name = f'{author.last_name}, {author.first_name}'
        actual_object_name = str(author)
        self.assertEqual(actual_object_name, expected_object_name)

    def test_get_absolute_url(self):
        author = Author.objects.get(id=1)
        # This will also fail if the urlconf is not defined.
        author_expected_url = '/catalog/author/1'
        author_actual_url = author.get_absolute_url()
        self.assertEqual(author_actual_url, author_expected_url)

# Tests related to the model named Genre
class GenreModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        Genre.objects.create(name = 'Science Fiction')  # Create an instance that will be used in all the methods 
    
    def test_name_max_length(self):
        genre = Genre.objects.get(id = 1)
        name_expected_max_length = 100
        name_actual_max_length = genre._meta.get_field(field_name = 'name').max_length
        self.assertEqual(name_actual_max_length, name_expected_max_length)

    def test_name_help_text(self):
        genre = Genre.objects.get(id = 1)
        help_text_expected_value = 'Enter a book genre (e.g. Science Fiction)'
        help_text_actual_value = genre._meta.get_field(field_name = 'name').help_text
        self.assertEqual(help_text_actual_value, help_text_expected_value)

    def test_object_name_is_name_field(self):
        genre = Genre.objects.get(id = 1)
        object_actual_name = genre.name
        object_expected_name = str(genre)
        self.assertEqual(object_actual_name, object_expected_name)

# Tests related to the model named Language
class LanguageModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        Language.objects.create(name = 'Anglais')
    
    def test_name_max_length(self):
        language = Language.objects.get(id = 1)
        name_expected_max_length = 50
        name_actual_max_length = language._meta.get_field(field_name='name').max_length
        self.assertEqual(name_actual_max_length, name_expected_max_length)
    
    def test_name_help_text(self):
        language = Language.objects.get(id = 1)
        name_expected_help_text = "Enter the book's natural language (e.g. English, French, Japanese, etc.)"
        name_actual_help_text = language._meta.get_field(field_name='name').help_text
        self.assertEqual(name_actual_help_text, name_expected_help_text)

    def test_object_name_is_name_field(self):
        language = Language.objects.get(id = 1)
        object_expected_name = language.name
        object_actual_name = str(language)
        self.assertEqual(object_actual_name, object_expected_name)

# Tests related to the model named Book
class BookModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        Author.objects.create(first_name = 'Massa Makan', last_name = 'Diabate')
        author1 = Author.objects.get(id = 1)
        Genre.objects.create(name = 'French Poetry')
        genre1 = Genre.objects.get(id = 1)
        Language.objects.create(name = 'Spanish')
        language1 = Language.objects.get(id = 1)
        summary = 'This is just an example of summary'
        Book.objects.create(title = "Le coiffeur de Koufa", author = author1, summary = summary, isbn = 'ABCD XYZ 1234', language = language1)
        book1 = Book.objects.get(id = 1)
        book1.genre.add(genre1) 

    def test_title_max_length(self):
        book = Book.objects.get(id = 1)
        title_expected_max_length = 200
        title_actual_max_length = book._meta.get_field(field_name='title').max_length
        self.assertEqual(title_actual_max_length, title_expected_max_length)

    def test_author_null_property(self):
        book = Book.objects.get(id = 1)
        null_property_expected_value = True
        null_property_actual_value = book._meta.get_field(field_name='author').null
        self.assertEqual(null_property_actual_value, null_property_expected_value)

    def test_summary_max_length(self):
        book = Book.objects.get(id = 1)
        summary_expected_max_lenght = 1000
        summary_actual_max_lenght = book._meta.get_field(field_name='summary').max_length
        self.assertEqual(summary_actual_max_lenght, summary_expected_max_lenght)

    def test_summary_help_text(self):
        book = Book.objects.get(id = 1)
        summary_expected_help_text = 'Enter a brief description of the book'
        summary_actual_help_text = book._meta.get_field(field_name = 'summary').help_text
        self.assertEqual(summary_actual_help_text, summary_expected_help_text)

    def test_isbn_verbose_name(self):
        book = Book.objects.get(id = 1)
        isbn_expected_verbose_name = 'ISBN'
        isbn_actual_verbose_name = book._meta.get_field(field_name='isbn').verbose_name
        self.assertEqual(isbn_actual_verbose_name, isbn_expected_verbose_name)

    def test_isbn_max_length(self):
        book = Book.objects.get(id = 1)
        isbn_expected_max_length = 13
        isbn_actual_max_length = book._meta.get_field(field_name='isbn').max_length
        self.assertEqual(isbn_actual_max_length, isbn_expected_max_length)
    
    def test_isbn_help_text(self):
        book = Book.objects.get(id = 1)
        isbn_expected_help_text = '13 Character <a href="https://www.isbn-international.org/content/what-isbn">ISBN number</a>'
        isbn_actual_help_text = book._meta.get_field(field_name='isbn').help_text
        self.assertEqual(isbn_actual_help_text, isbn_expected_help_text)
    
    def test_genre_help_text(self):
        book = Book.objects.get(id = 1)
        genre_expected_help_text = 'Select a genre for this book'
        genre_actual_help_text = book._meta.get_field(field_name='genre').help_text
        self.assertEqual(genre_actual_help_text, genre_expected_help_text)

    def test_language_null_property(self):
        book = Book.objects.get(id = 1)
        null_property_expected_value = True
        null_property_actual_value = book._meta.get_field(field_name='language').null
        self.assertEqual(null_property_actual_value, null_property_expected_value)

    def test_object_name_is_book_title(self):
        book = Book.objects.get(id = 1)
        object_expected_name = book.title
        object_actual_name = str(book)
        self.assertEqual(object_actual_name, object_expected_name)

    def test_book_absolute_url(self):
        book = Book.objects.get(id = 1)
        book_expected_url = '/catalog/book/1'
        book_actual_url = book.get_absolute_url()
        self.assertEqual(book_actual_url, book_expected_url)

    def test_display_book_genre(self):
        book = Book.objects.get(id = 1)
        book_expected_genre = 'French Poetry'
        book_actual_genre = book.display_genre()
        self.assertEqual(book_actual_genre, book_expected_genre)

# Tests related to the model named BookInstance
class BookInstanceModelTest(TestCase):
    pass
