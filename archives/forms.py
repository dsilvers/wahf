from django import forms
from wagtail.admin.widgets import AdminTagWidget
from wagtail.images.forms import BaseImageForm

# https://stackoverflow.com/questions/70200660/how-to-customize-the-admin-form-for-a-custom-image-model-in-wagtail-cms


class WAHFImageAdminForm(BaseImageForm):
    class Meta:
        # set the 'file' widget to a FileInput rather than the default ClearableFileInput
        # so that when editing, we don't get the 'currently: ...' banner which is
        # a bit pointless here
        widgets = {
            "tags": AdminTagWidget,
            "file": forms.FileInput(),
            "focal_point_x": forms.HiddenInput(attrs={"class": "focal_point_x"}),
            "focal_point_y": forms.HiddenInput(attrs={"class": "focal_point_y"}),
            "focal_point_width": forms.HiddenInput(
                attrs={"class": "focal_point_width"}
            ),
            "focal_point_height": forms.HiddenInput(
                attrs={"class": "focal_point_height"}
            ),
        }

    def save(self, *args, **kwargs):
        return super().save(*args, **kwargs)
