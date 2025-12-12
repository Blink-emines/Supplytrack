from django.contrib import admin

from blog.models import Plant , Famille , Article , Appartenir_P_A , AO , DA , ISE , Cde , Fournisseur , Appartenir_A_I ,  Appartenir_A_D ,  Appartenir_A_A , Commander

admin.site.register(Plant)
admin.site.register(Famille)
admin.site.register(Article)
admin.site.register(Appartenir_P_A)
admin.site.register(AO)
admin.site.register(DA)
admin.site.register(ISE)
admin.site.register(Cde)
admin.site.register(Fournisseur)
admin.site.register(Appartenir_A_I)
admin.site.register(Appartenir_A_D)
admin.site.register(Appartenir_A_A)
admin.site.register(Commander)



from .models import ImportHistory

@admin.register(ImportHistory)
class ImportHistoryAdmin(admin.ModelAdmin):
    list_display = ['type_fichier', 'nom_fichier', 'date_import', 'nb_lignes_traitees', 'nb_erreurs', 'statut']
    list_filter = ['type_fichier', 'statut', 'date_import']
    search_fields = ['nom_fichier', 'details']
    readonly_fields = ['date_import']
    
    def has_add_permission(self, request):
        return False  # Empêcher l'ajout manuel