
import pandas as pd
from .utils import *
from blog.models import Plant, Famille, Article, AO, ISE, DA, Cde, Fournisseur, Appartenir_P_A, Appartenir_A_I, Appartenir_A_D, Appartenir_A_A, Commander, ImportHistory  # ← AJOUT

def process_ao_data(fichier):
    nb_lignes = 0
    nb_erreurs = 0
 
    
    try:
        df_ao = pd.read_excel(fichier)
        df_ao.drop_duplicates(inplace=True) 

        df_ao["DA"] = clean_decimal(df_ao["DA"])
        df_ao["AO"] = clean_text(df_ao["AO"])
        df_ao['Date AO'] = clean_date(df_ao['Date AO'])

        for _, row in df_ao.iterrows():
            try:
                nb_lignes += 1
                
                da_value = row["DA"]
                ao_value = row["AO"]
                date_ao = row["Date AO"]

                ao_obj, _ = AO.objects.get_or_create(id_AO=ao_value)
                da_obj, _ = DA.objects.get_or_create(
                    id_DA=da_value,
                    defaults={"ao": ao_obj}
                )
                
                articles_da = Appartenir_A_D.objects.filter(da=da_obj)

                for art in articles_da:
                    article_obj = art.article
                    link, _ = Appartenir_A_A.objects.get_or_create(
                    article=article_obj,
                    ao=ao_obj,
                )

                    if date_ao:
                        link.date_AO = date_ao
                        link.save()

                                   

            except DA.DoesNotExist:
                nb_erreurs += 1
                
            except Exception as e:
                nb_erreurs += 1
               
        # ✅ ENREGISTRER L'HISTORIQUE
        ImportHistory.objects.create(
            type_fichier='AO',
            nom_fichier=fichier.name,
            nb_lignes_traitees=nb_lignes,
            nb_erreurs=nb_erreurs,
            statut='SUCCESS' if nb_erreurs == 0 else ('PARTIAL' if nb_erreurs < nb_lignes else 'ERROR'),
            
        )
        
        print(f"✅ Import AO terminé : {nb_lignes} lignes, {nb_erreurs} erreurs")

    except Exception as e:
        ImportHistory.objects.create(
            type_fichier='AO',
            nom_fichier=fichier.name if hasattr(fichier, 'name') else 'Inconnu',
            nb_lignes_traitees=nb_lignes,
            nb_erreurs=nb_erreurs + 1,
            statut='ERROR',
            details=f"Erreur critique: {str(e)}"
        )
        print(f"❌ Erreur critique AO: {e}")