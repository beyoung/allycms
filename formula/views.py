import json
import random
from functools import lru_cache

from django.contrib import messages
from django.contrib.humanize.templatetags.humanize import intcomma
from django.forms import modelformset_factory
from django.urls import reverse_lazy
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from django.views.generic import FormView, RedirectView, ListView, DetailView, TemplateView
from django.views.generic.edit import CreateView
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q
from unfold.views import UnfoldModelAdminViewMixin

from formula.forms import (
    CustomForm,
    CustomHorizontalForm,
    DriverForm,
    DriverFormHelper,
    DriverFormSet,
    ContactForm,
    InquiryForm,
    MessageForm,
    NewsletterForm,
    SearchForm,
)
from formula.models import Driver, Article, Category, Page, Contact, Inquiry, Message, ContentStatus


class HomeView(RedirectView):
    pattern_name = "admin:index"


class CrispyFormView(UnfoldModelAdminViewMixin, FormView):
    title = _("Crispy form")  # required: custom page header title
    form_class = CustomForm
    success_url = reverse_lazy("admin:index")
    # required: tuple of permissions
    permission_required = (
        "formula.view_driver",
        "formula.add_driver",
        "formula.change_driver",
        "formula.delete_driver",
    )
    template_name = "formula/driver_crispy_form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["horizontal_form"] = CustomHorizontalForm()
        return context


class CrispyFormsetView(UnfoldModelAdminViewMixin, FormView):
    title = _("Crispy form with formset")  # required: custom page header title
    success_url = reverse_lazy("admin:crispy_formset")
    # required: tuple of permissions
    permission_required = (
        "formula.view_driver",
        "formula.add_driver",
        "formula.change_driver",
        "formula.delete_driver",
    )
    template_name = "formula/driver_crispy_formset.html"

    def get_form_class(self):
        return modelformset_factory(
            Driver, DriverForm, formset=DriverFormSet, extra=1, can_delete=True
        )

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update(
            {
                "queryset": Driver.objects.filter(code__in=["VER", "HAM"]),
            }
        )
        return kwargs

    def form_invalid(self, form):
        messages.error(self.request, _("Formset submitted with errors"))
        return super().form_invalid(form)

    def form_valid(self, form):
        messages.success(self.request, _("Formset submitted successfully"))
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context.update(
            {
                "driver_formset_helper": DriverFormHelper(),
            }
        )
        return context


def dashboard_callback(request, context):
    context.update(random_data())
    return context


@lru_cache
def random_data():
    WEEKDAYS = [
        "Mon",
        "Tue",
        "Wed",
        "Thu",
        "Fri",
        "Sat",
        "Sun",
    ]

    positive = [[1, random.randrange(8, 28)] for i in range(1, 28)]
    negative = [[-1, -random.randrange(8, 28)] for i in range(1, 28)]
    average = [r[1] - random.randint(3, 5) for r in positive]
    performance_positive = [[1, random.randrange(8, 28)] for i in range(1, 28)]
    performance_negative = [[-1, -random.randrange(8, 28)] for i in range(1, 28)]

    return {
        "navigation": [
            {"title": _("Dashboard"), "link": "/", "active": True},
            {"title": _("Analytics"), "link": "#"},
            {"title": _("Settings"), "link": "#"},
        ],
        "filters": [
            {"title": _("All"), "link": "#", "active": True},
            {
                "title": _("New"),
                "link": "#",
            },
        ],
        "kpi": [
            {
                "title": "Product A Performance",
                "metric": f"${intcomma(f'{random.uniform(1000, 9999):.02f}')}",
                "footer": mark_safe(
                    f'<strong class="text-green-700 font-semibold dark:text-green-400">+{intcomma(f"{random.uniform(1, 9):.02f}")}%</strong>&nbsp;progress from last week'
                ),
                "chart": json.dumps(
                    {
                        "labels": [WEEKDAYS[day % 7] for day in range(1, 28)],
                        "datasets": [{"data": average, "borderColor": "#9333ea"}],
                    }
                ),
            },
            {
                "title": "Product B Performance",
                "metric": f"${intcomma(f'{random.uniform(1000, 9999):.02f}')}",
                "footer": mark_safe(
                    f'<strong class="text-green-700 font-semibold dark:text-green-400">+{intcomma(f"{random.uniform(1, 9):.02f}")}%</strong>&nbsp;progress from last week'
                ),
            },
            {
                "title": "Product C Performance",
                "metric": f"${intcomma(f'{random.uniform(1000, 9999):.02f}')}",
                "footer": mark_safe(
                    f'<strong class="text-green-700 font-semibold dark:text-green-400">+{intcomma(f"{random.uniform(1, 9):.02f}")}%</strong>&nbsp;progress from last week'
                ),
            },
        ],
        "progress": [
            {
                "title": "Social marketing e-book",
                "description": f"${intcomma(f'{random.uniform(1000, 9999):.02f}')}",
                "value": random.randint(10, 90),
            },
            {
                "title": "Freelancing tasks",
                "description": f"${intcomma(f'{random.uniform(1000, 9999):.02f}')}",
                "value": random.randint(10, 90),
            },
            {
                "title": "Development coaching",
                "description": f"${intcomma(f'{random.uniform(1000, 9999):.02f}')}",
                "value": random.randint(10, 90),
            },
            {
                "title": "Product consulting",
                "description": f"${intcomma(f'{random.uniform(1000, 9999):.02f}')}",
                "value": random.randint(10, 90),
            },
            {
                "title": "Other income",
                "description": f"${intcomma(f'{random.uniform(1000, 9999):.02f}')}",
                "value": random.randint(10, 90),
            },
            {
                "title": "Course sales",
                "description": f"${intcomma(f'{random.uniform(1000, 9999):.02f}')}",
                "value": random.randint(10, 90),
            },
            {
                "title": "Ads revenue",
                "description": f"${intcomma(f'{random.uniform(1000, 9999):.02f}')}",
                "value": random.randint(10, 90),
            },
            {
                "title": "Customer Retention Rate",
                "description": f"${intcomma(f'{random.uniform(1000, 9999):.02f}')}",
                "value": random.randint(10, 90),
            },
        ],
        "chart": json.dumps(
            {
                "labels": [WEEKDAYS[day % 7] for day in range(1, 28)],
                "datasets": [
                    {
                        "label": "Example 1",
                        "type": "line",
                        "data": average,
                        "borderColor": "var(--color-primary-500)",
                    },
                    {
                        "label": "Example 2",
                        "data": positive,
                        "backgroundColor": "var(--color-primary-700)",
                    },
                    {
                        "label": "Example 3",
                        "data": negative,
                        "backgroundColor": "var(--color-primary-300)",
                    },
                ],
            }
        ),
        "performance": [
            {
                "title": _("Last week revenue"),
                "metric": "$1,234.56",
                "footer": mark_safe(
                    '<strong class="text-green-600 font-medium">+3.14%</strong>&nbsp;progress from last week'
                ),
                "chart": json.dumps(
                    {
                        "labels": [WEEKDAYS[day % 7] for day in range(1, 28)],
                        "datasets": [
                            {
                                "data": performance_positive,
                                "borderColor": "var(--color-primary-700)",
                            }
                        ],
                    }
                ),
            },
            {
                "title": _("Last week expenses"),
                "metric": "$1,234.56",
                "footer": mark_safe(
                    '<strong class="text-green-600 font-medium">+3.14%</strong>&nbsp;progress from last week'
                ),
                "chart": json.dumps(
                    {
                        "labels": [WEEKDAYS[day % 7] for day in range(1, 28)],
                        "datasets": [
                            {
                                "data": performance_negative,
                                "borderColor": "var(--color-primary-300)",
                            }
                        ],
                    }
                ),
            },
        ],
        "table_data": {
            "headers": [_("Day"), _("Income"), _("Expenses")],
            "rows": [
                ["22-10-2025", "$2,341.89", "$1,876.45"],
                ["23-10-2025", "$1,987.23", "$2,109.67"],
                ["24-10-2025", "$3,456.78", "$1,543.21"],
                ["25-10-2025", "$1,765.43", "$2,987.65"],
                ["26-10-2025", "$2,876.54", "$1,234.56"],
                ["27-10-2025", "$1,543.21", "$2,765.43"],
                ["28-10-2025", "$3,210.98", "$1,987.65"],
            ],
        },
    }


######################################################################
# CMS Views
######################################################################

class ArticleListView(ListView):
    """文章列表视图"""
    model = Article
    template_name = "formula/cms/article_list.html"
    context_object_name = "articles"
    paginate_by = 10
    
    def get_queryset(self):
        queryset = Article.objects.filter(status=ContentStatus.PUBLISHED)
        
        # 分类过滤
        category_slug = self.request.GET.get("category")
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        
        # 搜索过滤
        search_query = self.request.GET.get("q")
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(content__icontains=search_query) |
                Q(excerpt__icontains=search_query)
            )
        
        return queryset.select_related("category", "author").prefetch_related("tags")
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = Category.objects.filter(is_active=True)
        context["search_form"] = SearchForm(self.request.GET)
        context["featured_articles"] = Article.objects.filter(
            status=ContentStatus.PUBLISHED,
            is_featured=True
        )[:5]
        return context


class ArticleDetailView(DetailView):
    """文章详情视图"""
    model = Article
    template_name = "formula/cms/article_detail.html"
    context_object_name = "article"
    
    def get_queryset(self):
        return Article.objects.filter(status=ContentStatus.PUBLISHED).select_related(
            "category", "author"
        ).prefetch_related("tags")
    
    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        # 增加浏览次数
        obj.view_count += 1
        obj.save(update_fields=["view_count"])
        return obj
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        article = self.get_object()
        
        # 相关文章
        context["related_articles"] = Article.objects.filter(
            status=ContentStatus.PUBLISHED,
            category=article.category
        ).exclude(id=article.id)[:3]
        
        # 最新文章
        context["latest_articles"] = Article.objects.filter(
            status=ContentStatus.PUBLISHED
        ).exclude(id=article.id)[:5]
        
        return context


class CategoryDetailView(DetailView):
    """分类详情视图"""
    model = Category
    template_name = "formula/cms/category_detail.html"
    context_object_name = "category"
    
    def get_queryset(self):
        return Category.objects.filter(is_active=True)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category = self.get_object()
        
        # 分页文章列表
        articles = Article.objects.filter(
            status=ContentStatus.PUBLISHED,
            category=category
        ).select_related("author").prefetch_related("tags")
        
        paginator = Paginator(articles, 10)
        page_number = self.request.GET.get("page")
        page_obj = paginator.get_page(page_number)
        
        context["page_obj"] = page_obj
        context["articles"] = page_obj.object_list
        return context


class PageDetailView(DetailView):
    """页面详情视图"""
    model = Page
    template_name = "formula/cms/page_detail.html"
    context_object_name = "page"
    
    def get_queryset(self):
        return Page.objects.filter(status=ContentStatus.PUBLISHED)
    
    def get_object(self, queryset=None):
        # 支持通过slug获取页面
        slug = self.kwargs.get("slug")
        if slug:
            return get_object_or_404(Page, slug=slug, status=ContentStatus.PUBLISHED)
        return super().get_object(queryset)


class HomePageView(TemplateView):
    """首页视图"""
    template_name = "formula/cms/home.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["featured_articles"] = Article.objects.filter(
            status=ContentStatus.PUBLISHED,
            is_featured=True
        )[:6]
        context["latest_articles"] = Article.objects.filter(
            status=ContentStatus.PUBLISHED
        )[:10]
        context["categories"] = Category.objects.filter(is_active=True).exclude(slug__isnull=True).exclude(slug="")[:8]
        return context


######################################################################
# Contact & Inquiry Views
######################################################################

class ContactView(CreateView):
    """联系表单视图"""
    model = Contact
    form_class = ContactForm
    template_name = "formula/contact/contact.html"
    success_url = reverse_lazy("contact_success")
    
    def form_valid(self, form):
        # 保存用户信息
        contact = form.save(commit=False)
        contact.ip_address = self.get_client_ip()
        contact.user_agent = self.request.META.get("HTTP_USER_AGENT", "")
        contact.save()
        
        messages.success(self.request, _("Your message has been sent successfully!"))
        return super().form_valid(form)
    
    def get_client_ip(self):
        x_forwarded_for = self.request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0]
        else:
            ip = self.request.META.get("REMOTE_ADDR")
        return ip


class InquiryView(CreateView):
    """询盘表单视图"""
    model = Inquiry
    form_class = InquiryForm
    template_name = "formula/contact/inquiry.html"
    success_url = reverse_lazy("inquiry_success")
    
    def form_valid(self, form):
        # 保存用户信息
        inquiry = form.save(commit=False)
        inquiry.ip_address = self.get_client_ip()
        inquiry.user_agent = self.request.META.get("HTTP_USER_AGENT", "")
        inquiry.save()
        
        messages.success(self.request, _("Your inquiry has been submitted successfully!"))
        return super().form_valid(form)
    
    def get_client_ip(self):
        x_forwarded_for = self.request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0]
        else:
            ip = self.request.META.get("REMOTE_ADDR")
        return ip


class MessageView(CreateView):
    """留言表单视图"""
    model = Message
    form_class = MessageForm
    template_name = "formula/contact/message.html"
    success_url = reverse_lazy("message_success")
    
    def form_valid(self, form):
        # 保存用户信息
        message = form.save(commit=False)
        message.ip_address = self.get_client_ip()
        message.user_agent = self.request.META.get("HTTP_USER_AGENT", "")
        message.save()
        
        messages.success(self.request, _("Your message has been sent successfully!"))
        return super().form_valid(form)
    
    def get_client_ip(self):
        x_forwarded_for = self.request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0]
        else:
            ip = self.request.META.get("REMOTE_ADDR")
        return ip


class ContactSuccessView(TemplateView):
    """联系成功页面"""
    template_name = "formula/contact/success.html"


class InquirySuccessView(TemplateView):
    """询盘成功页面"""
    template_name = "formula/contact/inquiry_success.html"


class MessageSuccessView(TemplateView):
    """留言成功页面"""
    template_name = "formula/contact/message_success.html"


def newsletter_subscribe(request):
    """订阅newsletter的AJAX视图"""
    if request.method == "POST":
        form = NewsletterForm(request.POST)
        if form.is_valid():
            # 这里可以添加订阅逻辑，比如保存到数据库或发送到邮件服务
            email = form.cleaned_data["email"]
            # TODO: 实现订阅逻辑
            return JsonResponse({"success": True, "message": _("Successfully subscribed!")})
        else:
            return JsonResponse({"success": False, "errors": form.errors})
    return JsonResponse({"success": False, "message": _("Invalid request method")})


def search_view(request):
    """搜索视图"""
    form = SearchForm(request.GET)
    results = []
    
    if form.is_valid():
        query = form.cleaned_data["q"]
        if query:
            # 搜索文章
            articles = Article.objects.filter(
                Q(title__icontains=query) |
                Q(content__icontains=query) |
                Q(excerpt__icontains=query),
                status=ContentStatus.PUBLISHED
            ).select_related("category", "author")
            
            # 搜索页面
            pages = Page.objects.filter(
                Q(title__icontains=query) |
                Q(content__icontains=query),
                status=ContentStatus.PUBLISHED
            )
            
            results = list(articles) + list(pages)
    
    # 分页
    paginator = Paginator(results, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    
    context = {
        "form": form,
        "page_obj": page_obj,
        "results": page_obj.object_list,
        "query": request.GET.get("q", ""),
    }
    
    return render(request, "formula/cms/search_results.html", context)


######################################################################
# Media Upload Views
######################################################################

from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from formula.models import Media
import os


@method_decorator(csrf_exempt, name='dispatch')
class MediaUploadView(View):
    """媒体文件上传视图"""
    
    def post(self, request, *args, **kwargs):
        try:
            if 'file' not in request.FILES:
                return JsonResponse({
                    'success': False,
                    'error': 'No file provided'
                })
            
            uploaded_file = request.FILES['file']
            title = request.POST.get('title', uploaded_file.name)
            
            # 创建媒体对象
            media = Media.objects.create(
                title=title,
                file=uploaded_file,
                uploaded_by=request.user if request.user.is_authenticated else None
            )
            
            return JsonResponse({
                'success': True,
                'media': {
                    'id': media.id,
                    'title': media.title,
                    'url': media.file.url,
                    'file_type': media.file_type,
                    'file_size': media.file_size
                }
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })


class MediaBrowserView(ListView):
    """媒体浏览器视图"""
    model = Media
    template_name = 'formula/admin/media_browser.html'
    context_object_name = 'media_list'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Media.objects.all().order_by('-created_at')
        
        # 按文件类型过滤
        file_type = self.request.GET.get('file_type')
        if file_type:
            if file_type == 'image':
                queryset = queryset.filter(file_type__in=['.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg', '.bmp'])
            elif file_type == 'video':
                queryset = queryset.filter(file_type__in=['.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm', '.mkv'])
            elif file_type == 'audio':
                queryset = queryset.filter(file_type__in=['.mp3', '.wav', '.ogg', '.aac', '.flac', '.wma'])
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['file_type'] = self.request.GET.get('file_type', '')
        return context
