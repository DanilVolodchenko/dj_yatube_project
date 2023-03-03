from django.contrib import admin

from .models import Post, Group, Comment


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('pk', 'text', 'pub_date', 'author', 'group')
    search_fields = ('text',)
    list_filter = ('pub_date',)
    empty_value_display = '-пусто-'
    list_editable = ('group',)
    list_display_links = ('pk', 'text')  # дает ссылку на пост
    sortable_by = ('pk',)


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('pk', 'title', 'slug', 'description')
    search_fields = ('title',)
    empty_value_display = '-пусто-'


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('pk', 'author', 'text', 'created')
    list_filter = ('created',)
    search_fields = ('text',)
    empty_value_display = '-пусто-'


# admin.site.register(Post, PostAdmin)
# admin.site.register(Group, GroupAdmin)
# admin.site.register(Comment, CommentAdmin)
