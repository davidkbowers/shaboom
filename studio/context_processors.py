def studio_context(request):
    """
    Add the studio object to the template context if the user is a studio owner.
    """
    context = {}
    if hasattr(request, 'user') and request.user.is_authenticated and hasattr(request.user, 'studio_profile'):
        context['studio'] = request.user.studio_profile
    return context
