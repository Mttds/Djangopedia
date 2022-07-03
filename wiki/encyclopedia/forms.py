from django import forms

class AddEntryForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # add bootstrap form-control class to each field
        for f in self.fields:
            self.fields[f].widget.attrs['class'] = 'form-control'

    title = forms.CharField(label="Title", max_length=50)
    content = forms.CharField(widget=forms.Textarea)

class EditEntryForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # add bootstrap form-control class to each field
        for f in self.fields:
            self.fields[f].widget.attrs['class'] = 'form-control'

    content = forms.CharField(widget=forms.Textarea)
