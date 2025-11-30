from django.contrib import admin
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import path, include

def index(request):
    # Option 1: a simple text message
    # return HttpResponse("Smart Task Analyzer backend is running. Use /api/tasks/analyze/ to POST tasks.")

    # Option 2: redirect to React dev server (change port if needed)
    return HttpResponseRedirect("http://127.0.0.1:5173/")

urlpatterns = [
    path('', index, name='index'),
    path('admin/', admin.site.urls),
    path('api/tasks/', include('tasks.urls')),
]
