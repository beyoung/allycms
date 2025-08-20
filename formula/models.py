from django.contrib.auth.models import AbstractUser
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import gettext_lazy as _
from djmoney.models.fields import MoneyField
from simple_history.models import HistoricalRecords
from django.utils.text import slugify

from formula.encoders import PrettyJSONEncoder


class DriverStatus(models.TextChoices):
    ACTIVE = "ACTIVE", _("Active")
    INACTIVE = "INACTIVE", _("Inactive")


class DriverCategory(models.TextChoices):
    ROOKIE = "ROOKIE", _("Rookie")
    EXPERIENCED = "EXPERIENCED", _("Experienced")
    VETERAN = "VETERAN", _("Veteran")
    CHAMPION = "CHAMPION", _("Champion")


class AuditedModel(models.Model):
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    modified_at = models.DateTimeField(_("modified at"), auto_now=True)

    class Meta:
        abstract = True


class Tag(AuditedModel):
    title = models.CharField(_("title"), max_length=255)
    slug = models.CharField(_("slug"), max_length=255)
    content_type = models.ForeignKey(
        ContentType, on_delete=models.CASCADE, verbose_name=_("content type")
    )
    object_id = models.PositiveIntegerField(_("object id"))
    content_object = GenericForeignKey("content_type", "object_id")

    def __str__(self):
        return self.tag

    class Meta:
        db_table = "tags"
        verbose_name = _("tag")
        verbose_name_plural = _("tags")
        indexes = [
            models.Index(fields=["content_type", "object_id"]),
        ]


class User(AbstractUser, AuditedModel):
    biography = models.TextField(_("biography"), null=True, blank=True, default=None)
    tags = GenericRelation(Tag)

    class Meta:
        db_table = "users"
        verbose_name = _("user")
        verbose_name_plural = _("users")

    def __str__(self):
        return self.email if self.email else self.username

    @property
    def full_name(self):
        if self.first_name and self.last_name:
            return f"{self.last_name}, {self.first_name}"

        return None


class Profile(AuditedModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    picture = models.ImageField(_("picture"), null=True, blank=True, default=None)
    resume = models.FileField(_("resume"), null=True, blank=True, default=None)
    link = models.URLField(_("link"), null=True, blank=True)
    data = models.JSONField(_("data"), null=True, blank=True)

    class Meta:
        db_table = "profiles"
        verbose_name = _("profile")
        verbose_name_plural = _("profiles")


class Circuit(AuditedModel):
    name = models.CharField(_("name"), max_length=255)
    city = models.CharField(_("city"), max_length=255)
    country = models.CharField(_("country"), max_length=255)
    data = models.JSONField(_("data"), null=True, blank=True)

    class Meta:
        db_table = "circuits"
        verbose_name = _("circuit")
        verbose_name_plural = _("circuits")

    def __str__(self):
        return self.name


class Driver(AuditedModel):
    first_name = models.CharField(_("first name"), max_length=255)
    last_name = models.CharField(_("last name"), max_length=255)
    salary = MoneyField(
        max_digits=14, decimal_places=2, null=True, blank=True, default_currency=None
    )
    category = models.CharField(
        _("category"),
        choices=DriverCategory.choices,
        null=True,
        blank=True,
        max_length=255,
    )
    picture = models.ImageField(_("picture"), null=True, blank=True, default=None)
    born_at = models.DateField(_("born"), null=True, blank=True)
    last_race_at = models.DateField(_("last race"), null=True, blank=True)
    best_time = models.TimeField(_("best time"), null=True, blank=True)
    first_race_at = models.DateTimeField(_("first race"), null=True, blank=True)
    resume = models.FileField(_("resume"), null=True, blank=True, default=None)
    author = models.ForeignKey(
        "User",
        verbose_name=_("author"),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    editor = models.ForeignKey(
        "User",
        verbose_name=_("editor"),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="driver_editor",
    )
    standing = models.ForeignKey(
        "Standing",
        verbose_name=_("standing"),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="standing",
    )
    constructors = models.ManyToManyField(
        "Constructor", verbose_name=_("constructors"), blank=True
    )
    code = models.CharField(_("code"), max_length=3)
    color = models.CharField(_("color"), null=True, blank=True, max_length=255)
    link = models.URLField(_("link"), null=True, blank=True)
    status = models.CharField(
        _("status"),
        choices=DriverStatus.choices,
        null=True,
        blank=True,
        max_length=255,
    )
    conditional_field_active = models.CharField(
        _("conditional field active"),
        null=True,
        blank=True,
        max_length=255,
        help_text="This field is only visible if the status is ACTIVE",
    )
    conditional_field_inactive = models.CharField(
        _("conditional field inactive"),
        null=True,
        blank=True,
        max_length=255,
        help_text="This field is only visible if the status is INACTIVE",
    )
    data = models.JSONField(_("data"), null=True, blank=True, encoder=PrettyJSONEncoder)
    history = HistoricalRecords()
    is_active = models.BooleanField(_("active"), default=False)
    is_retired = models.BooleanField(
        _("retired"),
        choices=(
            (None, ""),
            (True, _("Active")),
            (False, _("Inactive")),
        ),
        null=True,
    )
    is_hidden = models.BooleanField(_("hidden"), default=False)

    class Meta:
        db_table = "drivers"
        verbose_name = _("driver")
        verbose_name_plural = _("drivers")
        permissions = (("update_statistics", _("Update statistics")),)

    def __str__(self):
        return self.full_name

    @property
    def full_name(self):
        if self.first_name and self.last_name:
            return f"{self.last_name}, {self.first_name}"

        return None

    @property
    def initials(self):
        if self.first_name and self.last_name:
            return f"{self.first_name[0]}{self.last_name[0]}"

        return None


class DriverWithFilters(Driver):
    history = HistoricalRecords()

    class Meta:
        proxy = True


class Constructor(AuditedModel):
    name = models.CharField(_("name"), max_length=255)

    class Meta:
        db_table = "constructors"
        verbose_name = _("constructor")
        verbose_name_plural = _("constructors")

    def __str__(self):
        return self.name


class Race(AuditedModel):
    circuit = models.ForeignKey(
        Circuit, verbose_name=_("circuit"), on_delete=models.PROTECT
    )
    winner = models.ForeignKey(
        Driver, verbose_name=_("winner"), on_delete=models.PROTECT
    )
    picture = models.ImageField(_("picture"), null=True, blank=True, default=None)
    year = models.PositiveIntegerField(_("year"))
    laps = models.PositiveIntegerField(_("laps"))
    date = models.DateField(_("date"))
    weight = models.PositiveIntegerField(_("weight"), default=0, db_index=True)

    class Meta:
        db_table = "races"
        verbose_name = _("race")
        verbose_name_plural = _("races")
        ordering = ["weight"]

    def __str__(self):
        return f"{self.circuit.name}, {self.year}"


class Standing(AuditedModel):
    race = models.ForeignKey(Race, verbose_name=_("race"), on_delete=models.PROTECT)
    driver = models.ForeignKey(
        Driver,
        verbose_name=_("driver"),
        on_delete=models.PROTECT,
        related_name="standings",
    )
    constructor = models.ForeignKey(
        Constructor, verbose_name=_("constructor"), on_delete=models.PROTECT
    )
    position = models.PositiveIntegerField(_("position"))
    number = models.PositiveIntegerField(_("number"))
    laps = models.PositiveIntegerField(_("laps"))
    points = models.DecimalField(_("points"), decimal_places=2, max_digits=4)
    weight = models.PositiveIntegerField(_("weight"), default=0, db_index=True)

    class Meta:
        db_table = "standings"
        verbose_name = _("standing")
        verbose_name_plural = _("standings")
        ordering = ["weight"]

    def __str__(self):
        return f"{self.driver.full_name}, {self.position}"


######################################################################
# CMS Content Management Models
######################################################################


class ContentStatus(models.TextChoices):
    DRAFT = "DRAFT", _("Draft")
    PUBLISHED = "PUBLISHED", _("Published")
    ARCHIVED = "ARCHIVED", _("Archived")


class Category(AuditedModel):
    name = models.CharField(_("name"), max_length=255)
    slug = models.SlugField(_("slug"), max_length=255, unique=True)
    description = models.TextField(_("description"), blank=True)
    parent = models.ForeignKey(
        "self",
        verbose_name=_("parent category"),
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="children",
    )
    image = models.ImageField(_("image"), null=True, blank=True)
    is_active = models.BooleanField(_("active"), default=True)
    order = models.PositiveIntegerField(_("order"), default=0)

    class Meta:
        db_table = "cms_categories"
        verbose_name = _("category")
        verbose_name_plural = _("categories")
        ordering = ["order", "name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            # Handle Chinese characters and other non-ASCII characters
            import re
            import unicodedata
            
            # Convert to ASCII-friendly string
            name = self.name
            # Normalize unicode characters
            name = unicodedata.normalize('NFKD', name)
            # Remove non-ASCII characters and replace with spaces
            name = re.sub(r'[^\x00-\x7F]+', ' ', name)
            # Generate slug
            self.slug = slugify(name)
            # If slug is still empty, use a fallback
            if not self.slug:
                self.slug = f"category-{self.id}" if self.id else "category"
        super().save(*args, **kwargs)


class Article(AuditedModel):
    title = models.CharField(_("title"), max_length=255)
    slug = models.SlugField(_("slug"), max_length=255, unique=True)
    content = models.TextField(_("content"))
    excerpt = models.TextField(_("excerpt"), blank=True)
    featured_image = models.ImageField(_("featured image"), null=True, blank=True)
    category = models.ForeignKey(
        Category,
        verbose_name=_("category"),
        on_delete=models.CASCADE,
        related_name="articles",
    )
    author = models.ForeignKey(
        User,
        verbose_name=_("author"),
        on_delete=models.CASCADE,
        related_name="articles",
    )
    status = models.CharField(
        _("status"),
        max_length=20,
        choices=ContentStatus.choices,
        default=ContentStatus.DRAFT,
    )
    published_at = models.DateTimeField(_("published at"), null=True, blank=True)
    meta_title = models.CharField(_("meta title"), max_length=255, blank=True)
    meta_description = models.TextField(_("meta description"), blank=True)
    meta_keywords = models.CharField(_("meta keywords"), max_length=255, blank=True)
    is_featured = models.BooleanField(_("featured"), default=False)
    view_count = models.PositiveIntegerField(_("view count"), default=0)
    tags = GenericRelation(Tag)

    class Meta:
        db_table = "cms_articles"
        verbose_name = _("article")
        verbose_name_plural = _("articles")
        ordering = ["-published_at", "-created_at"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            # Handle Chinese characters and other non-ASCII characters
            import re
            import unicodedata
            
            # Convert to ASCII-friendly string
            title = self.title
            # Normalize unicode characters
            title = unicodedata.normalize('NFKD', title)
            # Remove non-ASCII characters and replace with spaces
            title = re.sub(r'[^\x00-\x7F]+', ' ', title)
            # Generate slug
            self.slug = slugify(title)
            # If slug is still empty, use a fallback
            if not self.slug:
                self.slug = f"article-{self.id}" if self.id else "article"
        if self.status == ContentStatus.PUBLISHED and not self.published_at:
            from django.utils import timezone

            self.published_at = timezone.now()
        super().save(*args, **kwargs)


class Page(AuditedModel):
    title = models.CharField(_("title"), max_length=255)
    slug = models.SlugField(_("slug"), max_length=255, unique=True)
    content = models.TextField(_("content"))
    template = models.CharField(_("template"), max_length=255, default="default")
    status = models.CharField(
        _("status"),
        max_length=20,
        choices=ContentStatus.choices,
        default=ContentStatus.DRAFT,
    )
    published_at = models.DateTimeField(_("published at"), null=True, blank=True)
    meta_title = models.CharField(_("meta title"), max_length=255, blank=True)
    meta_description = models.TextField(_("meta description"), blank=True)
    meta_keywords = models.CharField(_("meta keywords"), max_length=255, blank=True)
    is_homepage = models.BooleanField(_("homepage"), default=False)
    order = models.PositiveIntegerField(_("order"), default=0)

    class Meta:
        db_table = "cms_pages"
        verbose_name = _("page")
        verbose_name_plural = _("pages")
        ordering = ["order", "title"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            # Handle Chinese characters and other non-ASCII characters
            import re
            import unicodedata
            
            # Convert to ASCII-friendly string
            title = self.title
            # Normalize unicode characters
            title = unicodedata.normalize('NFKD', title)
            # Remove non-ASCII characters and replace with spaces
            title = re.sub(r'[^\x00-\x7F]+', ' ', title)
            # Generate slug
            self.slug = slugify(title)
            # If slug is still empty, use a fallback
            if not self.slug:
                self.slug = f"page-{self.id}" if self.id else "page"
        if self.status == ContentStatus.PUBLISHED and not self.published_at:
            from django.utils import timezone

            self.published_at = timezone.now()
        super().save(*args, **kwargs)


class Media(AuditedModel):
    title = models.CharField(_("title"), max_length=255)
    file = models.FileField(_("file"), upload_to="cms/media/")
    file_type = models.CharField(_("file type"), max_length=50, blank=True)
    file_size = models.PositiveIntegerField(_("file size"), null=True, blank=True)
    alt_text = models.CharField(_("alt text"), max_length=255, blank=True)
    description = models.TextField(_("description"), blank=True)
    uploaded_by = models.ForeignKey(
        User,
        verbose_name=_("uploaded by"),
        on_delete=models.CASCADE,
        related_name="uploaded_media",
    )

    class Meta:
        db_table = "cms_media"
        verbose_name = _("media")
        verbose_name_plural = _("media")
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if self.file:
            import os

            self.file_type = os.path.splitext(self.file.name)[1].lower()
            self.file_size = self.file.size
        super().save(*args, **kwargs)


######################################################################
# Contact & Inquiry Models
######################################################################


class InquiryStatus(models.TextChoices):
    NEW = "NEW", _("New")
    IN_PROGRESS = "IN_PROGRESS", _("In Progress")
    RESPONDED = "RESPONDED", _("Responded")
    CLOSED = "CLOSED", _("Closed")


class Contact(AuditedModel):
    name = models.CharField(_("name"), max_length=255)
    email = models.EmailField(_("email"))
    phone = models.CharField(_("phone"), max_length=20, blank=True)
    subject = models.CharField(_("subject"), max_length=255)
    message = models.TextField(_("message"))
    ip_address = models.GenericIPAddressField(_("IP address"), null=True, blank=True)
    user_agent = models.TextField(_("user agent"), blank=True)
    is_read = models.BooleanField(_("read"), default=False)
    responded_at = models.DateTimeField(_("responded at"), null=True, blank=True)
    response_message = models.TextField(_("response message"), blank=True)
    responded_by = models.ForeignKey(
        User,
        verbose_name=_("responded by"),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="contact_responses",
    )

    class Meta:
        db_table = "contacts"
        verbose_name = _("contact")
        verbose_name_plural = _("contacts")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} - {self.subject}"


class Inquiry(AuditedModel):
    name = models.CharField(_("name"), max_length=255)
    email = models.EmailField(_("email"))
    phone = models.CharField(_("phone"), max_length=20, blank=True)
    company = models.CharField(_("company"), max_length=255, blank=True)
    product_interest = models.CharField(
        _("product interest"), max_length=255, blank=True
    )
    quantity = models.PositiveIntegerField(_("quantity"), null=True, blank=True)
    budget = models.CharField(_("budget"), max_length=100, blank=True)
    message = models.TextField(_("message"))
    status = models.CharField(
        _("status"),
        max_length=20,
        choices=InquiryStatus.choices,
        default=InquiryStatus.NEW,
    )
    ip_address = models.GenericIPAddressField(_("IP address"), null=True, blank=True)
    user_agent = models.TextField(_("user agent"), blank=True)
    assigned_to = models.ForeignKey(
        User,
        verbose_name=_("assigned to"),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_inquiries",
    )
    notes = models.TextField(_("notes"), blank=True)
    responded_at = models.DateTimeField(_("responded at"), null=True, blank=True)
    response_message = models.TextField(_("response message"), blank=True)
    responded_by = models.ForeignKey(
        User,
        verbose_name=_("responded by"),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="inquiry_responses",
    )

    class Meta:
        db_table = "inquiries"
        verbose_name = _("inquiry")
        verbose_name_plural = _("inquiries")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} - {self.product_interest}"


class Message(AuditedModel):
    name = models.CharField(_("name"), max_length=255)
    email = models.EmailField(_("email"))
    subject = models.CharField(_("subject"), max_length=255, blank=True)
    message = models.TextField(_("message"))
    ip_address = models.GenericIPAddressField(_("IP address"), null=True, blank=True)
    user_agent = models.TextField(_("user agent"), blank=True)
    is_read = models.BooleanField(_("read"), default=False)
    is_spam = models.BooleanField(_("spam"), default=False)
    responded_at = models.DateTimeField(_("responded at"), null=True, blank=True)
    response_message = models.TextField(_("response message"), blank=True)
    responded_by = models.ForeignKey(
        User,
        verbose_name=_("responded by"),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="message_responses",
    )

    class Meta:
        db_table = "messages"
        verbose_name = _("message")
        verbose_name_plural = _("messages")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} - {self.subject or 'No Subject'}"
