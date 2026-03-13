from django import forms
from Lines.models.Line import Line


class FormItem(forms.Form):
    lines = Line.objects.all()
    items = forms.ModelMultipleChoiceField(
        queryset=lines,
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )
    print(items)
