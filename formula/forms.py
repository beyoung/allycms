from crispy_forms.helper import FormHelper
from crispy_forms.layout import Column, Div, Fieldset, Layout, Row
from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.views.generic import RedirectView
from unfold.forms import AuthenticationForm
from unfold.layout import Submit
from unfold.widgets import (
    UnfoldAdminCheckboxSelectMultiple,
    UnfoldAdminDateWidget,
    UnfoldAdminEmailInputWidget,
    UnfoldAdminExpandableTextareaWidget,
    UnfoldAdminFileFieldWidget,
    UnfoldAdminImageFieldWidget,
    UnfoldAdminIntegerFieldWidget,
    UnfoldAdminMoneyWidget,
    UnfoldAdminRadioSelectWidget,
    UnfoldAdminSelect2Widget,
    UnfoldAdminSplitDateTimeWidget,
    UnfoldAdminTextareaWidget,
    UnfoldAdminTextInputWidget,
    UnfoldAdminTimeWidget,
    UnfoldAdminURLInputWidget,
    UnfoldBooleanSwitchWidget,
)

from formula.models import Driver, Contact, Inquiry, Message
from unfold.contrib.forms.widgets import WysiwygWidget


class HomeView(RedirectView):
    pattern_name = "admin:index"


class CustomFormMixin(forms.Form):
    name = forms.CharField(
        max_length=100,
        label=_("Name"),
        required=True,
        widget=UnfoldAdminTextInputWidget(),
    )
    email = forms.EmailField(
        label=_("Email"),
        required=True,
        widget=UnfoldAdminEmailInputWidget(),
    )
    age = forms.IntegerField(
        label=_("Age"),
        required=True,
        min_value=18,
        max_value=120,
        widget=UnfoldAdminIntegerFieldWidget(),
    )
    url = forms.URLField(
        label=_("URL"),
        required=True,
        widget=UnfoldAdminURLInputWidget(),
    )
    salary = forms.DecimalField(
        label=_("Salary"),
        required=True,
        help_text=_("Enter your salary"),
        widget=UnfoldAdminMoneyWidget(),
    )
    title = forms.CharField(
        label=_("Title"),
        required=True,
        widget=UnfoldAdminExpandableTextareaWidget(),
    )
    message = forms.CharField(
        label=_("Message"),
        required=True,
        widget=UnfoldAdminTextareaWidget(),
    )
    subscribe = forms.BooleanField(
        label=_("Subscribe to newsletter"),
        required=True,
        initial=True,
        help_text=_("Toggle to receive our newsletter with updates and offers"),
        widget=UnfoldBooleanSwitchWidget,
    )
    notifications = forms.BooleanField(
        label=_("Receive notifications"),
        required=True,
        initial=False,
        help_text=_("Toggle to receive notifications about your inquiry status"),
        widget=UnfoldBooleanSwitchWidget,
    )
    department = forms.ChoiceField(
        label=_("Department"),
        choices=[
            ("sales", _("Sales")),
            ("marketing", _("Marketing")),
            ("development", _("Development")),
            ("hr", _("Human Resources")),
            ("other", _("Other")),
        ],
        required=True,
        help_text=_("Select the department to contact"),
        widget=UnfoldAdminRadioSelectWidget,
    )
    category = forms.ChoiceField(
        label=_("Category"),
        choices=[
            ("general", _("General Inquiry")),
            ("support", _("Technical Support")),
            ("feedback", _("Feedback")),
            ("other", _("Other")),
        ],
        required=True,
        help_text=_("Select the category of your message"),
        widget=UnfoldAdminCheckboxSelectMultiple,
    )
    priority = forms.TypedChoiceField(
        label=_("Priority"),
        choices=[
            (1, _("Low")),
            (2, _("Medium")),
            (3, _("High")),
        ],
        coerce=int,
        required=True,
        initial=2,
        help_text=_("Select the priority of your message"),
        widget=UnfoldAdminSelect2Widget,
    )
    date = forms.DateField(
        label=_("Date"),
        required=True,
        widget=UnfoldAdminDateWidget,
    )
    time = forms.TimeField(
        label=_("Time"),
        required=True,
        widget=UnfoldAdminTimeWidget,
    )
    datetime = forms.SplitDateTimeField(
        label=_("Date and Time"),
        required=True,
        widget=UnfoldAdminSplitDateTimeWidget,
    )
    file = forms.FileField(
        label=_("File"),
        required=True,
        widget=UnfoldAdminFileFieldWidget,
    )
    image = forms.ImageField(
        label=_("Image"),
        required=True,
        widget=UnfoldAdminImageFieldWidget,
    )


class CustomHorizontalForm(CustomFormMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = "form-horizontal"
        self.helper.layout = Layout(
            Fieldset(
                _("Custom horizontal form"),
                "name",
                "email",
                "age",
                "url",
                "salary",
                "title",
                "message",
                "subscribe",
                "notifications",
                "department",
                "category",
                "date",
                "time",
                "datetime",
            ),
        )


class CustomForm(CustomFormMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.add_input(Submit("submit", _("Submit")))
        self.helper.add_input(Submit("submit", _("Submit 2")))
        self.helper.add_input(Submit("submit", _("Submit 3")))
        self.helper.attrs = {
            "novalidate": "novalidate",
        }
        self.helper.layout = Layout(
            Row(
                Column(
                    Fieldset(
                        _("Custom form"),
                        Column(
                            Row(
                                Div("name", css_class="w-1/2"),
                                Div("email", css_class="w-1/2"),
                            ),
                            Row(
                                Div("age", css_class="w-1/2"),
                                Div("url", css_class="w-1/2"),
                            ),
                            "salary",
                            "priority",
                            css_class="gap-5",
                        ),
                    ),
                    Fieldset(
                        _("Textarea & expandable textarea widgets"),
                        "title",
                        "message",
                    ),
                    css_class="lg:w-1/2",
                ),
                Column(
                    Fieldset(
                        _("Radio & checkbox widgets"),
                        Column(
                            "subscribe",
                            "notifications",
                            Row(
                                Div("department", css_class="w-1/2"),
                                Div("category", css_class="w-1/2"),
                            ),
                            css_class="gap-5",
                        ),
                    ),
                    Fieldset(
                        _("File upload widgets"),
                        Column(
                            "file",
                            "image",
                            css_class="gap-5",
                        ),
                    ),
                    Fieldset(
                        _("Date & time widgets"),
                        Column(
                            "date",
                            "time",
                            "datetime",
                            css_class="gap-5",
                        ),
                    ),
                    css_class="lg:w-1/2",
                ),
                css_class="mb-8",
            ),
        )


class DriverFormHelper(FormHelper):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.template = "unfold_crispy/layout/table_inline_formset.html"
        self.form_id = "driver-formset"
        self.form_add = True
        self.form_show_labels = False
        self.attrs = {
            "novalidate": "novalidate",
        }
        self.add_input(Submit("submit", _("Another submit")))
        self.add_input(Submit("submit", _("Submit")))


class DriverForm(forms.ModelForm):
    class Meta:
        model = Driver
        fields = "__all__"


class DriverFormSet(forms.BaseModelFormSet):
    def clean(self):
        super().clean()
        for form in self.forms:
            if form.cleaned_data and not form.cleaned_data.get("DELETE"):
                if not form.cleaned_data.get("first_name"):
                    form.add_error("first_name", _("First name is required."))


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        # Extract request from kwargs if present (for UnfoldAdminSite compatibility)
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        from django.conf import settings

        self.fields["username"].initial = settings.LOGIN_USERNAME
        self.fields["password"].initial = settings.LOGIN_PASSWORD


######################################################################
# Rich Text Editor with Multimedia Support
######################################################################

class RichTextWidget(WysiwygWidget):
    """支持多媒体的富文本编辑器"""
    
    def __init__(self, attrs=None):
        if attrs is None:
            attrs = {}
        
        # 配置富文本编辑器的多媒体支持
        attrs.update({
            'data-media-upload-url': '/admin/formula/media/upload/',
            'data-media-browse-url': '/admin/formula/media/browser/',
            'data-image-upload-url': '/admin/formula/media/upload/',
            'data-video-upload-url': '/admin/formula/media/upload/',
            'data-audio-upload-url': '/admin/formula/media/upload/',
        })
        
        super().__init__(attrs)
    
    class Media:
        css = {
            'all': (
                'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css',
                'css/rich-text-multimedia.css',
            )
        }
        js = (
            'https://cdnjs.cloudflare.com/ajax/libs/jquery/3.6.0/jquery.min.js',
            'js/rich-text-multimedia.js',
        )


######################################################################
# Contact & Inquiry Forms
######################################################################

class ContactForm(forms.ModelForm):
    """联系表单"""
    
    class Meta:
        model = Contact
        fields = ["name", "email", "phone", "subject", "message"]
        widgets = {
            "name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": _("Your name")
            }),
            "email": forms.EmailInput(attrs={
                "class": "form-control",
                "placeholder": _("Your email")
            }),
            "phone": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": _("Your phone number (optional)")
            }),
            "subject": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": _("Subject")
            }),
            "message": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 5,
                "placeholder": _("Your message")
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({"required": "required"})


class InquiryForm(forms.ModelForm):
    """询盘表单"""
    
    class Meta:
        model = Inquiry
        fields = [
            "name", "email", "phone", "company", 
            "product_interest", "quantity", "budget", "message"
        ]
        widgets = {
            "name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": _("Your name")
            }),
            "email": forms.EmailInput(attrs={
                "class": "form-control",
                "placeholder": _("Your email")
            }),
            "phone": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": _("Your phone number")
            }),
            "company": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": _("Your company name")
            }),
            "product_interest": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": _("Product you're interested in")
            }),
            "quantity": forms.NumberInput(attrs={
                "class": "form-control",
                "placeholder": _("Quantity needed"),
                "min": 1
            }),
            "budget": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": _("Your budget range")
            }),
            "message": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 5,
                "placeholder": _("Additional details about your inquiry")
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 设置必填字段
        required_fields = ["name", "email", "product_interest", "message"]
        for field_name in required_fields:
            if field_name in self.fields:
                self.fields[field_name].widget.attrs.update({"required": "required"})


class MessageForm(forms.ModelForm):
    """留言表单"""
    
    class Meta:
        model = Message
        fields = ["name", "email", "subject", "message"]
        widgets = {
            "name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": _("Your name")
            }),
            "email": forms.EmailInput(attrs={
                "class": "form-control",
                "placeholder": _("Your email")
            }),
            "subject": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": _("Subject (optional)")
            }),
            "message": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 5,
                "placeholder": _("Your message")
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 设置必填字段
        required_fields = ["name", "email", "message"]
        for field_name in required_fields:
            if field_name in self.fields:
                self.fields[field_name].widget.attrs.update({"required": "required"})


class NewsletterForm(forms.Form):
    """订阅表单"""
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            "class": "form-control",
            "placeholder": _("Enter your email address")
        })
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["email"].widget.attrs.update({"required": "required"})


class SearchForm(forms.Form):
    """搜索表单"""
    q = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": _("Search..."),
            "type": "search"
        })
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["q"].widget.attrs.update({"required": "required"})
