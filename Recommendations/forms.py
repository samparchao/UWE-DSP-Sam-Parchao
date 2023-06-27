from django import forms
from Recommendations.models import Topic

class TopicForm(forms.ModelForm):
    class Meta:
        model = Topic
        fields = ['name']