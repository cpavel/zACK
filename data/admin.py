import os

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse, path
from django.http import HttpResponse
from django.shortcuts import redirect

from zACK.helpers import LOGS_DIR
from zACK.tasks import SEARCH_TERM_LOG_FILE_NAME
from leads.helpers import RESULTS_FILE_NAME, RESULTS_DIR

from data import models
from zACK.tasks import async_search_term_by_id
from .models import Campaign


@admin.action(description="Start search")
def start_search(modeladmin, request, queryset):
    for search_term_wrapper in queryset:
        search_term_wrapper.start_search()


@admin.register(models.SearchTerm)
class SearchTermAdmin(admin.ModelAdmin):
    list_display = (
        "term",
        "run_status",
        "updated_at",
        "id",
        "location",
        "record_actions",
    )
    readonly_fields = ("run_status",)

    def start_search(self, request, object_id, *args, **kwargs):
        search_term = self.get_object(request, object_id)

        search_term.run_status = "Queued"
        async_search_term_by_id.delay(object_id)
        search_term.save()

        referrer = request.META.get("HTTP_REFERER")

        return redirect(referrer)

    def download_logs(self, request, object_id, *args, **kwargs):
        log_file_path = SEARCH_TERM_LOG_FILE_NAME.format(LOGS_DIR, object_id)

        try:
            with open(log_file_path, "r") as file:
                file_content = file.read()
        except FileNotFoundError:
            file_content = "No logs found"

        # Download logs as text
        return HttpResponse(file_content, content_type="text/plain")

    def download_results(self, request, object_id, *args, **kwargs):
        result_file_path = RESULTS_FILE_NAME.format(RESULTS_DIR, object_id)

        file_content = ""
        try:
            with open(result_file_path, "rb") as file:
                file_content = file.read()
        except FileNotFoundError:
            pass

        if file_content == "":
            # if file not found, return .txt file with "No results found" message
            result_file_path = os.path.splitext(result_file_path)[0] + ".txt"

            response = HttpResponse(
                "No results found", content_type="text/plain"
            )
            response["Content-Disposition"] = (
                f'attachment; filename="{os.path.basename(result_file_path)}"'
            )
        else:
            response = HttpResponse(
                file_content, content_type="application/octet-stream"
            )
            response["Content-Disposition"] = (
                f'attachment; filename="{os.path.basename(result_file_path)}"'
            )

        return response

    # Define URL for custom actions
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                r"<path:object_id>/start-search/",
                self.admin_site.admin_view(self.start_search),
                name="start-search",
            ),
            path(
                r"<path:object_id>/download-results/",
                self.admin_site.admin_view(self.download_results),
                name="download-results",
            ),
            path(
                r"<path:object_id>/download-logs/",
                self.admin_site.admin_view(self.download_logs),
                name="download-logs",
            ),
        ]
        return custom_urls + urls

    def record_actions(self, obj):
        return format_html(
            (
                '<a class="button" href="{}">Start</a>&nbsp;<a class="button"'
                ' href="{}">Results</a>&nbsp;<a class="button" href="{}"'
                ' target="_blank">Logs</a>&nbsp;'
            ),
            reverse("admin:start-search", args=[obj.pk]),
            reverse("admin:download-results", args=[obj.pk]),
            reverse("admin:download-logs", args=[obj.pk]),
        )

    record_actions.short_description = "Start | Download"
    record_actions.allow_tags = True


@admin.register(models.PromptTemplate)
class PromptTemplateAdmin(admin.ModelAdmin):
    list_display = (
        "template",
        "min_profile_length",
        "max_profile_length",
        "id",
    )


@admin.register(models.EvaluationTemplate)
class EvaluationTemplateAdmin(admin.ModelAdmin):
    list_display = ("template", "id")


@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'created_at', 'updated_at')
    search_fields = ('name',)


# TODO: This is not used. Remove all related code.
# admin.site.register(models.PromptResponse)
