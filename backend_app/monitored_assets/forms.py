from django import forms


class ImportMonitoredForm(forms.Form):
    owner_id = forms.HiddenInput()
    file = forms.CharField(widget=forms.FileInput())
