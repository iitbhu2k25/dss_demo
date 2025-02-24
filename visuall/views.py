from django.shortcuts import render
from django.http import JsonResponse

# Create your views here.
def visual_home(request):
    return render(request,'visuall/base.html')
    