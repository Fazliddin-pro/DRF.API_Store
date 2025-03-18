from django.shortcuts import render
from django.http import HttpResponse
from django.db.models.aggregates import Max, Count

from store.models import Customer, Product
from tags.models import TaggedItem

def say_hello(request):
    TaggedItem.objects.get_tags_for(Product, 1)

    return render(request, 'hello.html', {'name': 'Ali', 'products': product})