from django.shortcuts import render


def custom_403(request, exception):
    return render(request, 'errors/403.html', status=403)
