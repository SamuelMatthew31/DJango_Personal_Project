from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.contrib import messages
from django.views.decorators.http import require_POST

from .models import Task
from .forms import TaskForm


def dashboard(request):
    status_counts = Task.objects.values("status").annotate(count=Count("id"))
    counts = {item["status"]: item["count"] for item in status_counts}
    upcoming = Task.objects.exclude(status=Task.Status.COMPLETED).order_by("due_date")[:5]

    context = {
        "total": Task.objects.count(),
        "todo_count": counts.get(Task.Status.TODO, 0),
        "in_progress_count": counts.get(Task.Status.IN_PROGRESS, 0),
        "completed_count": counts.get(Task.Status.COMPLETED, 0),
        "upcoming": upcoming,
    }
    return render(request, "tasks/dashboard.html", context)


def task_list(request):
    tasks = Task.objects.all()

    query = request.GET.get("q", "")
    status = request.GET.get("status", "")
    priority = request.GET.get("priority", "")
    sort = request.GET.get("sort", "-created_at")

    if query:
        tasks = tasks.filter(Q(title__icontains=query) | Q(description__icontains=query))
    if status:
        tasks = tasks.filter(status=status)
    if priority:
        tasks = tasks.filter(priority=priority)
    if sort in ["due_date", "-due_date", "priority", "-priority", "-created_at"]:
        tasks = tasks.order_by(sort)

    paginator = Paginator(tasks, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj": page_obj,
        "query": query,
        "status": status,
        "priority": priority,
        "sort": sort,
        "status_choices": Task.Status.choices,
        "priority_choices": Task.Priority.choices,
    }

    # Kalau request datang dari HTMX, render partial saja (tanpa base.html)
    if request.headers.get("HX-Request"):
        return render(request, "tasks/_task_list_partial.html", context)

    return render(request, "tasks/task_list.html", context)


def task_detail(request, pk):
    task = get_object_or_404(Task, pk=pk)
    return render(request, "tasks/task_detail.html", {"task": task})


def task_create(request):
    if request.method == "POST":
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save()
            messages.success(request, "Task berhasil dibuat.")
            return redirect("tasks:task_detail", pk=task.pk)
    else:
        form = TaskForm()
    return render(request, "tasks/task_form.html", {"form": form, "mode": "create"})


def task_edit(request, pk):
    task = get_object_or_404(Task, pk=pk)
    if request.method == "POST":
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            messages.success(request, "Task berhasil diupdate.")
            return redirect("tasks:task_detail", pk=task.pk)
    else:
        form = TaskForm(instance=task)
    return render(request, "tasks/task_form.html", {"form": form, "mode": "edit", "task": task})


@require_POST
def task_delete(request, pk):
    task = get_object_or_404(Task, pk=pk)
    task.delete()
    messages.success(request, "Task berhasil dihapus.")
    return redirect("tasks:task_list")


@require_POST
def task_update_status(request, pk):
    task = get_object_or_404(Task, pk=pk)
    new_status = request.POST.get("status")
    if new_status in Task.Status.values:
        task.status = new_status
        task.save(update_fields=["status", "updated_at"])
    # Balikin partial kecil untuk HTMX swap (misal badge status doang)
    return render(request, "tasks/_status_badge.html", {"task": task})
