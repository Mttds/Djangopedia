from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from markdown2 import markdown
from random import randint
from . import util
from . import forms

def index(request):
    # check the ?q query parameter which means the user
    # searched for an entry in the search bar
    # check if that entry exists and return the page
    if request.GET.get('q') is not None:
        # If the query does not match the name of an encyclopedia entry,
        # the user should instead be taken to a search results page that displays
        # a list of all encyclopedia entries that have the query as a substring
        found_entries = []
        entry_exists = util.get_entry(request.GET.get('q'))

        if entry_exists is None:
            entries = util.list_entries()
            for entry in entries:
                print(f"Entry: {entry} | Query: {request.GET.get('q')}")
                if entry.lower().find(request.GET.get('q').lower()) != -1:
                    found_entries.append(entry)

        if len(found_entries) == 0 or entry_exists:
            # we found an exact match or no matches found
            return HttpResponseRedirect(reverse('encyclopedia:entry', kwargs={'title': request.GET.get('q')}))
        else:
            # we found some matching items and we want to display them to the user
            return render(request, "encyclopedia/index.html", {
                "entries": found_entries,
                "header1": "Found Pages"
            })

    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries(),
        "header1": "All Pages"
    })

def entry(request, title):
    entry = util.get_entry(title)
    content = "<h1>No Encyclopedia entry found.</h1>"

    if entry is not None:
        # found encyclopedia entry for the title provided
        content = markdown(entry)
    
    return render(request, "encyclopedia/entry.html", {
        "content": content,
        "title": title
    })

def edit(request, title):
    if request.method == "POST":
        form = forms.EditEntryForm(request.POST)
        if form.is_valid():
            content = form.cleaned_data["content"]

            # add the encyclopedia entry
            try:
                util.save_entry(title.lower().capitalize(), content)
            except PermissionError:
                # in WSL the Django default storage gives a permission denied error when it tries to do chmod
                # if the files are actually in the Windows filesystem and not in the WSL VM filesystem.
                # The files are creted nonetheless
                pass
            except Exception:
                return render(request, "encyclopedia/add.html", {
                    "form": form,
                    "error": f"Title = {title}. Something went wrong during the saving of the Encyclopedia entry."
                })

            # redirect the user to the edited entry
            return HttpResponseRedirect(reverse('encyclopedia:entry', kwargs={'title': title}))
        else:
            return render(request, "encyclopedia/add.html", {
                "form": form,
            })

    if request.method == "GET":
        content = util.get_entry(title)
        form = forms.EditEntryForm(initial={'content': content})
        
        return render(request, "encyclopedia/edit.html", {
            "form": form,
            "title": title
        })

def add(request):
    # during a POST request check if the form is valid
    # server side by passing the post data to the AddEntryForm class
    # if it's valid we will proceed to save the encyclopedia entry to disk
    # and redirect the user to the newly created entry page
    if request.method == "POST":
        form = forms.AddEntryForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"]
            content = form.cleaned_data["content"]
            
            if title.lower() in [entry.lower() for entry in util.list_entries()]:
                print(f"Title = {title}. Encyclopedia entry already exists for this title.")

                return render(request, "encyclopedia/add.html", {
                    "form": forms.AddEntryForm(),
                    "error": f"Title = {title}. Encyclopedia entry already exists for this title."
                })
            else:
                # add the encyclopedia entry
                try:
                    util.save_entry(title.lower().capitalize(), content)
                except PermissionError:
                    # in WSL the Django default storage gives a permission denied error when it tries to do chmod
                    # if the files are actually in the Windows filesystem and not in the WSL VM filesystem.
                    # The files are creted nonetheless
                    pass
                except Exception:
                    return render(request, "encyclopedia/add.html", {
                        "form": form,
                        "error": f"Title = {title}. Something went wrong during the saving of the Encyclopedia entry."
                    })

                # redirect the user to the created entry
                return HttpResponseRedirect(reverse('encyclopedia:entry', kwargs={'title': title}))
        else:
            return render(request, "encyclopedia/add.html", {
                "form": form,
            })

    # during a GET request render the form AddEntryForm
    if request.method == "GET":
        return render(request, "encyclopedia/add.html", {
            "form": forms.AddEntryForm()
        })

def random(request):
    entries = util.list_entries()
    n_entries = len(entries)
    n_entry = randint(0, n_entries - 1)

    entry = entries[n_entry]
    return HttpResponseRedirect(reverse('encyclopedia:entry', kwargs={'title': entry}))
