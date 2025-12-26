from django import forms

from blog.models import Comment, Post, User


class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ('text',)


class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        exclude = ('author', 'created_at')
        widgets = {
            'pub_date': forms.DateTimeInput(
                format='%Y-%m-%dT%H:%M', attrs={'type': 'datetime-local'}
            ),
            'is_published': forms.CheckboxInput(
                attrs={'class': 'form-check-input'}
            )
        }

        labels = {
            'is_published': 'Опубликовать пост'
        }
        help_texts = {
            'is_published': 'Снимите галочку, чтобы скрыть публикацию'
        }


class ProfileForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')
