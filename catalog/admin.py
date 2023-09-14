from django.contrib import admin

# Register your models here.
from .models import Author, Genre, Language, Book, BookInstance
admin.site.register(Genre)
admin.site.register(Language)

#Inline editing of associated records - Book in Author detail
class BooksInline(admin.TabularInline):
    model = Book

class AuthorAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name', 'date_of_birth', 'date_of_death')
    fields = ['first_name', 'last_name', ('date_of_birth', 'date_of_death')]
    inlines = [BooksInline]
admin.site.register(Author, AuthorAdmin)

#Inline editing of associated records - BookInstande in Book detail
class BooksInstanceInline(admin.TabularInline):
    model = BookInstance

# Register the Admin class for Book using the decorator
@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'display_genre')
    inlines = [BooksInstanceInline]

# Register the Admin class for BookInstance using the decorator
@admin.register(BookInstance)
class BookInstanceAdmin(admin.ModelAdmin):
    list_display = ('id', 'book_title', 'status', 'borrower', 'due_back')
    list_filter = ('status', 'due_back')
    fieldsets = (
        (
            None, {'fields': ('book', 'imprint', 'id')}
        ),
        (
            'Availability',{'fields': ('status', 'due_back', 'borrower')}
        )
    )