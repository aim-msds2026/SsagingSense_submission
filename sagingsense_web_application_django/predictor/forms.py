from django import forms


class ImageUploadForm(forms.Form):
    image = forms.ImageField(
        label="Image File",
        help_text="Upload a clear image for analysis.",
        widget=forms.ClearableFileInput(
            attrs={
                "class": "form-control",
                "accept": "image/*",
            }
        ),
    )
