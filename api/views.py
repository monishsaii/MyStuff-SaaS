from django.http import HttpResponse

def projects(request, organization_id):
    return HttpResponse("Organization = " + str(organization_id))