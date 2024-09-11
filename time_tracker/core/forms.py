from django import forms
from .models import Goal, Wish

class GoalForm(forms.ModelForm):
    start_time = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
        required=False
    )
    end_time = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
        required=False
    )

    class Meta:
        model = Goal
        fields = ['title', 'description', 'priority', 'estimated_time', 'due_date', 'start_time', 'end_time']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
            'estimated_time': forms.NumberInput(attrs={'class': 'form-control'}),
            'due_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

    def clean_estimated_time(self):
        estimated_time = self.cleaned_data.get('estimated_time')
        if estimated_time <= 0:
            raise forms.ValidationError("Estimated time must be a positive number.")
        return estimated_time


class WishForm(forms.ModelForm):
    class Meta:
        model = Wish
        fields = ['title', 'description']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your wish title'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter your wish description', 'rows': 4}),
        }
