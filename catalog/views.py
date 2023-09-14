import datetime

from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.db.models.query import QuerySet
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views import generic
from django.views.generic import CreateView, UpdateView, DeleteView

from typing import Any

from .forms import RenewBookForm
from .models import Author, Book, BookInstance, Genre

# Create your views here.

def index(request):
    """View function for home page of site."""

    # Generate counts of some of the main objects
    num_genres = Genre.objects.all().count()
    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()

    # Available books (status = 'a')
    num_instances_available = BookInstance.objects.filter(status__exact='a').count()

    # Books containing 'a' in the title
    num_books_with_a = Book.objects.filter(title__icontains = 'a').count()
    # The 'all()' is implied by default.
    num_authors = Author.objects.count()

    # Number of visits to this view, as counted in the session variable.
    num_visits = request.session.get("num_visits", 0)
    request.session["num_visits"] = num_visits + 1

    context = {
        'num_genres': num_genres,
        'num_books': num_books,
        'num_instances': num_instances,
        'num_instances_available': num_instances_available,
        'num_books_with_a': num_books_with_a,
        'num_authors': num_authors,
        "num_visits" : num_visits,
    }

    # Render the HTML template index.html with the data in the context variable
    return render(request, 'index.html', context=context)

class BookListView(generic.ListView):
    model = Book
    paginate_by = 5

class BookDetailView(generic.DetailView):
    model = Book

class AuthorListView(generic.ListView):
    model = Author
    paginate_by = 5

class AuthorDetailView(generic.DetailView):
    model = Author

class LoanedBooksByUserListView(LoginRequiredMixin, generic.ListView):
    """Generic class-based view listing books on loan to current user."""
    model = BookInstance
    paginate_by = 3
    template_name = 'catalog/bookinstance_list_borrowed_user.html'

    def get_queryset(self):
        return (
            BookInstance.objects.filter(borrower=self.request.user)
            .filter(status__exact='o')
            .order_by('due_back')
        )

class AllLoanedBooksListView(PermissionRequiredMixin, generic.ListView):
    """ Generic class based view to display all borrowed views """
    model = BookInstance
    permission_required = ('catalog.can_mark_returned',)
    template_name = 'catalog/bookinstance_list_borrowed_all.html'
    paginate_by = 5
    def get_queryset(self):
        return (
            BookInstance.objects.filter(status__exact = 'o')
            .order_by('due_back')
        )

@login_required
@permission_required('catalog.can_mark_returned', raise_exception=True)
def renew_book_librarian(request, pk):
    """View function for renewing a specific BookInstance by librarian."""
    book_instance = get_object_or_404(BookInstance, pk=pk)
    # If this is a POST request then process the Form data
    if request.method == 'POST':
        # Create a form instance and populate it with data from the request (binding):
        book_renewal_form = RenewBookForm(request.POST)
        # Check if the form is valid:
        if book_renewal_form.is_valid():
            # process the data in form.cleaned_data as required (here we just write it to the model due_back field)
            book_instance.due_back = book_renewal_form.cleaned_data['renewal_date']
            book_instance.save()
            # redirect to a new URL:
            return HttpResponseRedirect(reverse('all-borrowed'))
    # If this is a GET (or any other method) create the default form.
    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks = 3)
        book_renewal_form = RenewBookForm(initial = {'renewal_date': proposed_renewal_date})
    context = {
        'book_renewal_form': book_renewal_form,
        'book_instance': book_instance,
    }
    return render(request, 'catalog/book_renew_librarian.html', context)

class AuthorCreate(PermissionRequiredMixin, CreateView):
    model = Author
    permission_required = ('catalog.can_mark_returned',)
    fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death']
    initial = {'date_of_birth': datetime.date.today()}

class AuthorUpdate(PermissionRequiredMixin, UpdateView):
    model = Author
    permission_required = ('catalog.can_mark_returned',)
    fields = '__all__'  # Not recommanded for security issue if more fields in the future

class AuthorDelete(PermissionRequiredMixin, DeleteView):
    model = Author
    permission_required = ('catalog.can_mark_returned',)
    success_url = reverse_lazy('authors')   # lazy version of reverse because the URL goes to a class-based view

class BookCreate(PermissionRequiredMixin, CreateView):
    model = Book
    permission_required = ('catalog.can_edit_book',)
    fields = ['title', 'author', 'summary', 'isbn', 'genre', 'language']

class BookUpdate(PermissionRequiredMixin, UpdateView):
    model = Book
    permission_required = ('catalog.can_edit_book',)
    fields = ['title', 'author', 'summary', 'isbn', 'language']

class BookDelete(PermissionRequiredMixin, DeleteView):
    model = Book
    permission_required = ('catalog.can_delete_book',)
    success_url = reverse_lazy('books')
