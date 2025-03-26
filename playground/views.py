from django.shortcuts import render
from .tasks import notify_customers

def say_hello(request):
    notify_customers.delay('Hello there!')
    
    return render(request, 'hello.html', {'name': 'Ali'})