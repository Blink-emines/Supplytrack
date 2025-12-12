# blog/DATAtraitement/services.py

class DataService:
    """Service centralisé pour tous les traitements de données"""

    def process_ao(self, fichier):
        from .AO import process_ao_data
        return process_ao_data(fichier)

    def process_da(self, fichier):
        from .DA import process_da_data
        return process_da_data(fichier)

    def process_ise(self, fichier):
        from .ISE import process_ise_data
        return process_ise_data(fichier)

    def process_cde(self, fichier):
        # J'ai corrigé .Cde en .CMD pour correspondre à ton fichier CMD.py
        from .CMD import process_cde_data  
        return process_cde_data(fichier)
    def search_info(self, type_doc, code):
        # ICI : On importe tes fonctions avec leurs noms d'origine
        from .recherche import rechercher_ise, rechercher_da, rechercher_ao, rechercher_cmd

        if type_doc == 'ISE':
            return rechercher_ise(code)  # On appelle ta fonction
        elif type_doc == 'DA':
            return rechercher_da(code)   # On appelle ta fonction
        elif type_doc == 'AO':
            return rechercher_ao(code)   # On appelle ta fonction
        elif type_doc == 'CMD':
            return rechercher_cmd(code)  # On appelle ta fonction
        
        return None

# Singleton
data_service = DataService()