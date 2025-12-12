# blog/DATAtraitement/django_setup.py
import os
import sys
import django

def setup_django():
    """
    Configure Django quand DATAtraitement est dans blog
    """
    try:
        # Remonte de 2 niveaux : blog/DATAtraitement → blog → ikram
        current_dir = os.path.dirname(os.path.abspath(__file__))
        blog_dir = os.path.dirname(current_dir)  # blog/
        project_root = os.path.dirname(blog_dir) # ikram/
        
        sys.path.append(project_root)
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
        django.setup()
        
        print("Django configuré avec DATAtraitement dans blog!")
        return True
        
    except Exception as e:
        print(f"Erreur: {e}")
        return False