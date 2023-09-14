import datetime, uuid

# User is required to assign user as borrower.
# Permission is required to grant the premission needed to set a book as returned.
from django.contrib.auth.models import User, Permission
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from catalog.models import Author, Book, BookInstance, Genre, Language

class AuthorListViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create 13 authors for pagination tests (function run only once for all the test functions)
        number_of_authors = 13
        for author_id in range(number_of_authors):
            if(author_id % 2 == 0):
                Author.objects.create(
                    first_name=f'Dominique {author_id}',
                    last_name=f'Surname {author_id}',
                )
            else :
                Author.objects.create(
                    first_name=f'Lincoln {author_id}',
                    last_name=f'Bare {author_id}',
                )

    def test_view_url_exists_at_desired_location(self):
        response = self.client.get('/catalog/authors/')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse('authors'))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('authors'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'catalog/author_list.html')

    def test_pagination_is_five(self):
        response = self.client.get(reverse('authors'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('is_paginated' in response.context)
        self.assertTrue(response.context['is_paginated'] == True)
        self.assertEqual(len(response.context['author_list']), 5)   # will return the first page containing the first 5 authors in the list

    def test_lists_all_authors(self):
        # Get third page and confirm it has (exactly) remaining 3 items
        response = self.client.get(reverse('authors')+'?page=3')
        self.assertEqual(response.status_code, 200)
        self.assertTrue('is_paginated' in response.context)
        self.assertTrue(response.context['is_paginated'] == True)
        self.assertEqual(len(response.context['author_list']), 3)

class LoanedBooksByUserListViewTest(TestCase):
    def setUp(self):    # will be run before each test function
        # Create two users
        test_user1 = User.objects.create_user(username='testuser1', password='1X<ISRUkw+tuK')
        test_user2 = User.objects.create_user(username='testuser2', password='2HJ1vRV0Z&3iD')

        test_user1.save()
        test_user2.save()

        # Create a book
        test_author = Author.objects.create(first_name='John', last_name='Smith')
        Genre.objects.create(name='Fantasy')
        test_language = Language.objects.create(name='English')
        test_book = Book.objects.create(
            title='Book Title',
            summary='My book summary',
            isbn='ABCDEFG123456',
            author=test_author,
            language=test_language,
        )

        # Create genre as a post-step
        genre_objects_for_book = Genre.objects.all()
        test_book.genre.set(genre_objects_for_book) # Direct assignment of many-to-many types not allowed.
        test_book.save()

        # Create 30 BookInstance objects
        number_of_book_copies = 30
        for book_copy in range(number_of_book_copies):
            return_date = timezone.localtime() + datetime.timedelta(days=book_copy%5)
            the_borrower = test_user1 if book_copy % 2 else test_user2
            status = 'm'
            BookInstance.objects.create(
                book=test_book,
                imprint='Unlikely Imprint, 2016',
                due_back=return_date,
                borrower=the_borrower,
                status=status,
            )
   
    def test_redirect_if_not_logged_in(self):
        response = self.client.get('/catalog/mybooks/')
        self.assertRedirects(response, '/accounts/login/?next=/catalog/mybooks/')

    def test_view_url_exists_at_desired_location(self):
        loginStatus = self.client.login(username='testuser1', password='1X<ISRUkw+tuK')
        self.assertTrue(loginStatus)
        response = self.client.get('/catalog/mybooks/')
        self.assertEqual(response.status_code, 200)
        self.client.logout()

    def test_view_url_is_accessisble_by_name(self):
        loginStatus = self.client.login(username='testuser1', password='1X<ISRUkw+tuK')
        self.assertTrue(loginStatus)
        response = self.client.get(reverse('my-borrowed'))
        self.assertEqual(response.status_code, 200)
        self.client.logout()

    def test_logged_in_uses_correct_template(self):
        loginStatus = self.client.login(username='testuser1', password='1X<ISRUkw+tuK')
        self.assertTrue(loginStatus)
        response = self.client.get(reverse('my-borrowed'))
        # Check our user is logged in
        self.assertEqual(str(response.context['user']), 'testuser1')
        # Check that we got a response "success"
        self.assertEqual(response.status_code, 200)
        # Check we used correct template
        self.assertTemplateUsed(response, 'catalog/bookinstance_list_borrowed_user.html')
        self.client.logout()
  
    def test_pagination_is_three(self):
        userName = 'testuser1'
        userPassword = '1X<ISRUkw+tuK'
        loginStatus = self.client.login(username = userName, password = userPassword)
        self.assertTrue(loginStatus)    # the login process was successfull
        testuser = User.objects.get(username = 'testuser1')
        # Set the books assigned to current user to 'on loan'
        bookCopies = BookInstance.objects.all()
        for aBookCopy in bookCopies:
            if aBookCopy.borrower == testuser:
                aBookCopy.status = 'o'
                aBookCopy.save()
        response = self.client.get(reverse('my-borrowed'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('is_paginated' in response.context)
        self.assertTrue(response.context['is_paginated'] == True)
        self.assertTrue('bookinstance_list' in response.context)
        self.assertEqual(len(response.context['bookinstance_list']), 3) # will return the first page containing the first 3 bookinstances in the list
        self.client.logout()

    def test_only_books_borrowed_to_user_are_listed(self):
        loginStatus = self.client.login(username = 'testuser1', password = '1X<ISRUkw+tuK')
        self.assertTrue(loginStatus)
        response = self.client.get(reverse('my-borrowed'))
        # check the connected user is our user
        self.assertEqual(str(response.context['user']), 'testuser1')
        self.assertEqual(response.status_code, 200)
        # check that none of the current books is on loan (there are all on maintenance by default)
        self.assertTrue('bookinstance_list' in response.context)
        self.assertTrue(len(response.context['bookinstance_list']) == 0)

        # set all the book instances to on loan
        nb_init_books = len(BookInstance.objects.all())
        books = BookInstance.objects.all()[:nb_init_books/2] if nb_init_books >=2 else BookInstance.objects.all()
        for book in books:
            book.status = 'o'
            book.save()

        # now, check that some books are on loan
        response = self.client.get(reverse('my-borrowed'))
        self.assertEqual(str(response.context['user']), 'testuser1')
        self.assertEqual(response.status_code, 200)
        self.assertTrue('bookinstance_list' in response.context)
        self.assertFalse(len(response.context['bookinstance_list']) == 0)

        # check that the returned books belong to current user
        for bookItem in response.context['bookinstance_list']:
            self.assertTrue(bookItem.status == 'o')
            self.assertEqual(response.context['user'], bookItem.borrower)
        self.client.logout()

    def test_ordered_by_due_date(self):
        # change all the book instances to on loan
        books = BookInstance.objects.all()
        for bookItem in books:
            bookItem.status = 'o'
            bookItem.save()
        
        # login a user
        loginStatus = self.client.login(username = 'testuser1', password = '1X<ISRUkw+tuK')
        self.assertTrue(loginStatus)
        response = self.client.get(reverse('my-borrowed'))
        self.assertEqual(str(response.context['user']), 'testuser1')
        self.assertEqual(response.status_code, 200)

        # check that the books are ordered by date
        self.assertTrue('bookinstance_list' in response.context)
        self.assertTrue(len(response.context['bookinstance_list']) > 0)
        last_date = 0
        for bookItem in response.context['bookinstance_list']:
            if(last_date == 0):
                last_date = bookItem.due_back
            else:
                self.assertTrue(last_date >= bookItem.due_back)
                last_date = bookItem.due_back
        self.client.logout()


# Test the function-based view renew_book_librarian
class RenewBookInstanceViewsTest(TestCase):
    def setUp(self):
        # Create 2 users
        test_user1 = User.objects.create(username = 'test_user1')
        test_user1.set_password('1X<ISRUkw+tuK')
        test_user1.save()
        test_user2 = User.objects.create(username = 'test_user2')
        test_user2.set_password('2HJ1vRV0Z&3iD')
        test_user2.save()

        # Give test_user2 the permission to renew books
        permission_name = 'can_mark_returned' #'Set book as returned'
        model_name = ContentType.objects.get_for_model(BookInstance)
        renew_book_permission = Permission.objects.get(
            codename = permission_name, 
            content_type = model_name)
        if renew_book_permission:
            test_user2.user_permissions.add(renew_book_permission)
            test_user2.save()
        else:
            print('The permission was not found')

        # Create a book
        book_author = Author.objects.create(first_name = 'Dramane', last_name = 'SANGARE')
        test_language = Language.objects.create(name = 'English')
        test_book = Book.objects.create(
            title = 'Book Title',
            summary = 'My book summary',
            isbn = 'AZERTYUIOP123',
            author = book_author,
            language = test_language
        )
        # Set the genre as post step
        test_genre = Genre.objects.create(name = 'Fantasy')
        book_genres = Genre.objects.all()
        test_book.genre.set(book_genres)
        test_book.save()

        # Create a bookinstance object for test_user1
        return_date = datetime.date.today() + datetime.timedelta(days = 5)
        self.test_bookinstance1 = BookInstance.objects.create(
            book = test_book,
            imprint = 'Unlikely imprint, 2016',
            borrower = test_user1,
            due_back = return_date,
            status = 'o'
        )
        self.test_bookinstance2 = BookInstance.objects.create(
            book = test_book,
            imprint = 'Unlikely imprint, 2016',
            borrower = test_user2, 
            due_back = return_date,
            status = 'o'
        )
    
    def test_redirect_if_not_logged_in(self):
        bookinstance_id = self.test_bookinstance1.pk
        # response = self.client.get(f'/catalog/book/{bookinstance_id}/update/')
        response = self.client.get(reverse('renew-book-librarian', kwargs = {'pk': bookinstance_id}))
        # Manually the redirect because the assertRedirect function is not predictable
        self.assertEqual(response.status_code, 302) # 302 -> resource temporarily moved to the URI.
        self.assertTrue(response.url.startswith('/accounts/login/'))    # user redirected to login in

    def test_forbidden_if_logged_in_but_not_correct_permission(self):
        self.client.login(username = 'test_user1', password = '1X<ISRUkw+tuK')
        bookinstance_id = self.test_bookinstance1.pk
        response = self.client.get(reverse('renew-book-librarian', kwargs = {'pk': bookinstance_id}))
        self.assertTrue(response.status_code == 403 or response.status_code == 404) # the resource cannot be accessed by the user or does not exist

    def test_logged_in_with_permission_borrowed_book(self):
        longinStatus = self.client.login(username = 'test_user2', password = '2HJ1vRV0Z&3iD')
        self.assertTrue(longinStatus)
        bookinstance_id = self.test_bookinstance2.pk    # book instance 2 belongs to user2
        response = self.client.get(reverse('renew-book-librarian', kwargs = {'pk':bookinstance_id}))
        self.assertEqual(response.status_code, 200)

    def test_form_initial_date_is_3_weeks_in_future(self):
        userName = 'test_user2'
        uPassword = '2HJ1vRV0Z&3iD'
        loginStatus = self.client.login(username = userName, password = uPassword)
        self.assertTrue(loginStatus)
        bookinstance_id = self.test_bookinstance2.pk
        response = self.client.get(reverse('renew-book-librarian', kwargs = {'pk': bookinstance_id}))
        self.assertEqual(response.status_code, 200)
        form_expected_initial_date = datetime.date.today() + datetime.timedelta(weeks = 3)
        self.assertTrue('book_renewal_form' in response.context)
        self.assertTrue('renewal_date' in response.context['book_renewal_form'].initial)
        self.assertEqual(response.context['book_renewal_form'].initial['renewal_date'], form_expected_initial_date)
        self.client.logout()
    
    def test_logged_in_with_permission_another_users_borrowed_book(self):
        loginStatus = self.client.login(username = 'test_user2', password = '2HJ1vRV0Z&3iD')
        self.assertTrue(loginStatus)
        bookinstance_id = self.test_bookinstance1.pk    # book instance 1 belongs to user1
        response = self.client.get(reverse('renew-book-librarian', kwargs = {'pk': bookinstance_id}))
        self.assertEqual(response.status_code, 200) # can_mark_returned users can view books of any user

    def test_HTTP403or404_for_invalid_book_if_logged_in(self):
        loginStatus = self.client.login(username = 'test_user2', password = '2HJ1vRV0Z&3iD')
        self.assertTrue(loginStatus)
        bookinstance_id = uuid.uuid4()
        response = self.client.get(reverse('renew-book-librarian', kwargs = {'pk': bookinstance_id}))
        self.assertTrue(response.status_code == 403 or response.status_code == 404)    # The response status is different from 200 - success

    def test_uses_correct_template(self):
        loginStatus = self.client.login(username = 'test_user2', password = '2HJ1vRV0Z&3iD')
        self.assertTrue(loginStatus)
        bookinstance_id = self.test_bookinstance2.pk
        response = self.client.get(reverse('renew-book-librarian', kwargs = {'pk': bookinstance_id}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'catalog/book_renew_librarian.html')

    def test_form_invalid_date_in_past_error_msg(self):
        self.client.login(username = 'test_user2', password = '2HJ1vRV0Z&3iD')
        bookinstance_id = self.test_bookinstance2.pk
        form_proposed_date = datetime.date.today() - datetime.timedelta(weeks = 1)
        response = self.client.post(reverse('renew-book-librarian', kwargs = {'pk': bookinstance_id}), data = {'renewal_date': form_proposed_date})
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'book_renewal_form', 'renewal_date', 'Invalid date - renewal in the past.')

    def test_form_invalid_date_far_in_future_error_msg(self):
        self.client.login(username = 'test_user2', password = '2HJ1vRV0Z&3iD')
        bookinstance_id = self.test_bookinstance2.pk
        form_proposed_date = datetime.date.today() + datetime.timedelta(weeks = 8)
        response = self.client.post(reverse('renew-book-librarian', kwargs = {'pk': bookinstance_id}), data = {'renewal_date': form_proposed_date})
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response = response, form = 'book_renewal_form', field = 'renewal_date', errors = 'Invalid date - renewal date must be less than 4 weeks')

    def test_renew_book_redirects_to_all_borrowed_books_on_success(self):
        loginStatus = self.client.login(username = 'test_user2', password = '2HJ1vRV0Z&3iD')
        self.assertTrue(loginStatus)
        bookinstance_id = self.test_bookinstance2.pk
        form_proposed_date = datetime.date.today() + datetime.timedelta(weeks = 3)
        response = self.client.post(
            path = reverse('renew-book-librarian', kwargs = {'pk': bookinstance_id}), 
            data = {'renewal_date': form_proposed_date}, )
        self.assertRedirects(response, reverse('all-borrowed'))