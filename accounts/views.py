from django.http import HttpResponse
import json

def home(request):
    if request.method == 'GET':
        q = request.GET.get('name', 'Invalid')
        return HttpResponse("Hello from " + q)
    
    elif request.method == 'POST':
        data = json.loads(request.body)
        q = data.get('name')
        return HttpResponse("Hello from " + q)
    else:
        return HttpResponse("Method not allowed", status = 405)