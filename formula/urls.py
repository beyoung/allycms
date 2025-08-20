from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.urls import include, path

from formula.sites import formula_admin_site
from formula.views import (
    HomeView,
    # CMS Views
    HomePageView,
    ArticleListView,
    ArticleDetailView,
    CategoryDetailView,
    PageDetailView,
    # Contact Views
    ContactView,
    InquiryView,
    MessageView,
    ContactSuccessView,
    InquirySuccessView,
    MessageSuccessView,
    newsletter_subscribe,
    search_view,
    # Media Views
    MediaUploadView,
    MediaBrowserView,
)

urlpatterns = (
    [
        path("", HomePageView.as_view(), name="home"),
        path("admin-home/", HomeView.as_view(), name="admin_home"),
        path("i18n/", include("django.conf.urls.i18n")),
        path("__debug__/", include("debug_toolbar.urls")),
        
        # CMS URLs
        path("articles/", ArticleListView.as_view(), name="article_list"),
        path("article/<slug:slug>/", ArticleDetailView.as_view(), name="article_detail"),
        path("category/<slug:slug>/", CategoryDetailView.as_view(), name="category_detail"),
        path("page/<slug:slug>/", PageDetailView.as_view(), name="page_detail"),
        
        # Contact URLs
        path("contact/", ContactView.as_view(), name="contact"),
        path("inquiry/", InquiryView.as_view(), name="inquiry"),
        path("message/", MessageView.as_view(), name="message"),
        path("contact/success/", ContactSuccessView.as_view(), name="contact_success"),
        path("inquiry/success/", InquirySuccessView.as_view(), name="inquiry_success"),
        path("message/success/", MessageSuccessView.as_view(), name="message_success"),
        
        # AJAX URLs
        path("newsletter/subscribe/", newsletter_subscribe, name="newsletter_subscribe"),
        path("search/", search_view, name="search"),
        
        # Media URLs
        path("admin/formula/media/upload/", MediaUploadView.as_view(), name="media_upload"),
        path("admin/formula/media/browser/", MediaBrowserView.as_view(), name="media_browser"),
    ]
    + i18n_patterns(
        path("admin/", formula_admin_site.urls),
    )
    + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
)
