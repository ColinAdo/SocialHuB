from django.shortcuts import render


def home(request):
    template = 'core/index.html'
    
    context = {}
    return render(request, template, context)

