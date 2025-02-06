from django.shortcuts import render

# Create your views here.
def mapshow(request):
    """Render the main sewage estimation page."""
    return render(request, 'mapshow/base.html')