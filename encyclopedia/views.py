from django.shortcuts import render, HttpResponse,redirect
import markdown2 # Import the markdown2 library
from . import util
from django import forms
import random
def random_page(request):
    entries = util.list_entries()
    if entries:
        random_entry = random.choice(entries)
        return redirect("entry", title=random_entry)
    else:
        return redirect("index")  # Redirect to the index page if there are no entries

class EditPageForm(forms.Form):
    content = forms.CharField(widget=forms.Textarea(attrs={'rows': 10, 'cols': 60}), label="Content (Markdown)")

def edit_page(request, title):
    entry_content = util.get_entry(title)

    if entry_content is None:
        return HttpResponse("Page not found", status=404)

    if request.method == "POST":
        form = EditPageForm(request.POST)
        if form.is_valid():
            new_content = form.cleaned_data["content"]

            # Update the existing entry with the new content
            util.save_entry(title, new_content)

            # Redirect the user back to the entry's page
            return redirect("entry", title=title)
    else:
        form = EditPageForm(initial={"content": entry_content})

    return render(request, "encyclopedia/edit_page.html", {"title": title, "form": form})

class NewPageForm(forms.Form):
    title = forms.CharField(label="Title")
    content = forms.CharField(widget=forms.Textarea(attrs={'rows': 10, 'cols': 60}), label="Content (Markdown)")

def new_page(request):
    if request.method == "POST":
        form = NewPageForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"]
            content = form.cleaned_data["content"]

            # Check if an entry with the provided title already exists
            if util.get_entry(title):
                return HttpResponse("An entry with this title already exists.", status=400)

            # Save the new entry to disk
            util.save_entry(title, content)

            # Redirect the user to the new entry's page
            return redirect("entry", title=title)
    else:
        form = NewPageForm()

    return render(request, "encyclopedia/new_page.html", {"form": form})


def search(request):
    query = request.GET.get('q', '')  # Get the search query from the URL parameter 'q'
    entries = util.list_entries()

    # Filter entries that contain the query as a substring
    matching_entries = [entry for entry in entries if query.lower() in entry.lower()]

    return render(request, "encyclopedia/search_results.html", {"query": query, "entries": matching_entries})

def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

def entry(request, title):
    entry_content = util.get_entry(title)
    
    if title not in util.list_entries():
        return HttpResponse("404 : Page not found", status=404)
    
    # Convert Markdown to HTML using markdown2
    entry_content_html = markdown2.markdown(entry_content)

    return render(request, "encyclopedia/entry_page.html", {"title": title, "entry_content": entry_content_html})
