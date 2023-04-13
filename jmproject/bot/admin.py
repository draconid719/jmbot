from django.contrib import admin
from django.http import JsonResponse
from django.urls import path
import threading

from .bmodules.observableThread import ObservableThread
from .models import Bot
from .models import ArbitrageBot
from .models import Shout
from .models import Thread
from django.utils.translation import gettext_lazy as _
import time
from bot.views import start_thread, stop_thread, init_users, start_chart_thread, stop_chart_thread


class BotAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'profit', 'is_live')
    search_fields = ['name', 'profit']


def run_threads(request):
    try:
        if request.method == 'POST':
            if request.POST['action'] == 'start':
                init_users()
                start_chart_thread()
                time.sleep(5)
                start_thread()
                return JsonResponse({'status': 'started'})
            elif request.POST['action'] == 'stop':
                stop_thread()
                return JsonResponse({'status': 'ended'})
            elif request.POST['action'] == 'start-tick':
                init_users()
                start_chart_thread()
                time.sleep(5)
                return JsonResponse({'status': 'started tick'})
            elif request.POST['action'] == 'stop-tick':
                stop_chart_thread()
                time.sleep(5)
                return JsonResponse({'status': 'stopped tick'})

    except Exception as e:
        print(e)
        return JsonResponse({'error': str(e)})
    return JsonResponse({})


class ThreadAdmin(admin.ModelAdmin):
    list_display = ('bot', 'name', 'amount', 'mode', 'author', 'is_live', 'start_time')
    search_fields = ['bot__name', 'name', 'mode', 'author', 'start_time']
    actions = ['start_threads', 'stop_threads']

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('start_threads/', run_threads),
        ]
        return my_urls + urls

    def start_threads(self, request, queryset):
        init_users()
        start_chart_thread()
        time.sleep(5)
        start_thread(queryset)
    start_threads.short_description = _("Start selected threads")

    def stop_threads(self, request, queryset):
        time.sleep(5)
        stop_thread(queryset)
    stop_threads.short_description = _("Stop selected threads")

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        all_threads = threading.enumerate()
        result = [a for a in all_threads if type(a) is ObservableThread and a.name == 't_price' and a.is_running()]
        extra_context['tick'] = result
        return super(ThreadAdmin, self).changelist_view(
            request, extra_context=extra_context
        )


admin.site.register(Bot, BotAdmin)
admin.site.register(ArbitrageBot)
admin.site.register(Shout)
admin.site.register(Thread, ThreadAdmin)
