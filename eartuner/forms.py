from django import forms

class AudioUploadForm(forms.Form):
    audio_file = forms.FileField(label="Select your .m4a file", widget=forms.ClearableFileInput(attrs={'accept':'.m4a'}))
    difficulty = forms.IntegerField(min_value=0, max_value=50, initial=25)
