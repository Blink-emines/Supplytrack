# context_processors.py
page = 'dashboard'
def current_page(request):
    """Automatically determine current page from URL"""
    path = request.path.strip('/')
    
    if path == 'dashboard':
        page = 'dashboard'
    elif path == 'suivi-demandes' or path.startswith('suivi/detail/'):
        page = 'suivi'
    elif path == 'analyses':
        page = 'analyses'
    elif path == 'parametres':
        page = 'parametres'
    elif path == 'help':
        page = 'help'
    else:
        page = ''  # This ensures page is always defined
    
    return {'current_page': page}