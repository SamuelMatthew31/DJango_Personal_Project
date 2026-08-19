from django import forms
from django.utils import timezone
from .models import Task

INPUT_CLASS = (
    "w-full rounded-lg border border-slate-200 bg-slate-50 px-3 py-2 text-sm "
    "text-[#12161C] placeholder:text-slate-400 focus:border-[#0C8F87] "
    "focus:bg-white focus:outline-none"
)


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ["title", "description", "status", "priority", "due_date"]
        widgets = {
            "title": forms.TextInput(attrs={
                "class": INPUT_CLASS,
                "placeholder": "Judul task...",
            }),
            "description": forms.Textarea(attrs={
                "class": INPUT_CLASS,
                "rows": 4,
                "placeholder": "Deskripsi singkat (opsional)...",
            }),
            "status": forms.Select(attrs={"class": INPUT_CLASS}),
            "priority": forms.Select(attrs={"class": INPUT_CLASS}),
            "due_date": forms.DateInput(attrs={
                "class": INPUT_CLASS,
                "type": "date",
            }),
        }

    def clean_due_date(self):
        due_date = self.cleaned_data.get("due_date")
        if due_date and not self.instance.pk and due_date < timezone.now().date():
            raise forms.ValidationError("Due date tidak boleh di masa lalu.")
        return due_date

    def clean_title(self):
        title = self.cleaned_data.get("title", "").strip()
        if not title:
            raise forms.ValidationError("Title tidak boleh kosong.")
        return title
