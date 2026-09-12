from django.shortcuts import render


def robots_txt(request):
    """ Serve robots.txt with an absolute Sitemap URL for this host. """
    sitemap_url = request.build_absolute_uri('/sitemap.xml')
    return render(
        request,
        'robots.txt',
        {'sitemap_url': sitemap_url},
        content_type='text/plain',
    )


def handler403(request, exception=None):
    """ Error Handler 403 - Permission Denied """
    return render(request, 'errors/403.html', status=403)


def handler404(request, exception):
    """ Error Handler 404 - Page Not Found """
    return render(request, "errors/404.html", status=404)


def handler500(request):
    """ Error Handler 500 - Defaults Server Error """
    return render(request, 'errors/500.html', status=500)
