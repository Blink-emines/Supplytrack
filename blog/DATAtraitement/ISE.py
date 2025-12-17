import pandas as pd
from .utils import *
from blog.models import *

def process_ise_data(fichier):
    nb_lignes = 0
    nb_erreurs = 0
    
    try:
        df_besoin_1 = pd.read_excel(fichier, sheet_name=0)
        df_besoin_2 = pd.read_excel(fichier, sheet_name=1)

        df_besoin_1.drop_duplicates(inplace=True) 
        df_besoin_2.drop_duplicates(inplace=True) 
        df_besoin = pd.merge(df_besoin_1, df_besoin_2, on="ID ISE")
        
        df_besoin = df_besoin.drop(columns=['DA_x','plant_x','designation plant_x','Nombre de Code','Montant ISE_x'])

        # Nettoyage
        for c in ['Qte ISE', 'Montant ISE_y', 'PUMP']:
            df_besoin[c] = clean_decimal(df_besoin[c])

        for c in ['ID ISE', 'DA_y','plant_y', 'designation plant_y', 'Code', 'Désignaion', 'Udm', 'SF', 'Déstination']:
            df_besoin[c] = clean_text(df_besoin[c])
        
        df_besoin['Date ISE'] = clean_date(df_besoin['Date ISE'])

        for _, row in df_besoin.iterrows():
            try:
                nb_lignes += 1
                
                # Récupération de la DA si elle existe
                da_value = str(row["DA_y"]).strip() if pd.notna(row["DA_y"]) else None
                da_obj = None
                
                if da_value and da_value not in ['', 'nan', 'None', 'N/A']:
                    try:
                        da_obj = DA.objects.get(id_DA=da_value)
                    except DA.DoesNotExist:
                        pass

                # Création/récupération de l'ISE
                ise_obj, exist_ise = ISE.objects.get_or_create(
                    id_ise=row["ID ISE"],
                    defaults={"da": da_obj}
                )

                # Mise à jour de la DA si l'ISE existe déjà et n'a pas de DA
                if not exist_ise and da_obj is not None and ise_obj.da is None:
                    ise_obj.da = da_obj
                    ise_obj.save()

                # Création/récupération de la famille
                famille_obj, _ = Famille.objects.get_or_create(
                    designation_famille=row["SF"]
                )

                # Création/récupération de l'article
                article_obj, _ = Article.objects.get_or_create(
                    code_article=row["Code"],
                    defaults={
                        "designation_article": row["Désignaion"],
                        "udm": row["Udm"],
                        "famille": famille_obj
                    }
                )

                # Création/récupération du plant
                plant_obj, _ = Plant.objects.get_or_create(
                    code_plant=row["plant_y"],
                    defaults={"designation_plant": row["designation plant_y"]}
                )

                # Relation Plant-Article
                Appartenir_P_A.objects.get_or_create(
                    plant=plant_obj,
                    article=article_obj
                )
                
                # ✅ CORRECTION PRINCIPALE : Appartenir_A_I nécessite AO et Cde (non-null dans models)
                # Création d'un AO et d'une Cde par défaut si nécessaire
                
                # Récupérer ou créer un AO par défaut pour cet ISE
                
                
                
                # ✅ CORRECTION : Création de la relation Article-ISE avec tous les champs obligatoires
                rel_ise, created = Appartenir.objects.get_or_create(
                    article=article_obj,
                    ise=ise_obj,
                    defaults={
                        "da": da_obj,
                        "ao": None,  # ← Champ obligatoire (ForeignKey sans null=True)
                        "cde": None,  # ← Champ obligatoire (ForeignKey sans null=True)
                        "montant_ise": row["Montant ISE_y"],
                        "date_ise": row['Date ISE'],
                        "quantite_ise": row["Qte ISE"],
                        "montant_DA": None,
                        "date_DA": None,
                        "quantite_DA": None,
                        "date_AO": None ,
                        "fournisseur" : None,
                        "montant_Cde" : None,
                        "quantite_Cde" : None,
                        "date_Cde" :None,
                        "destination": row["Déstination"]
                    }
                )
                
                # ✅ Mise à jour du DA si l'enregistrement existe déjà et qu'un nouveau DA est disponible
                if not created and da_obj is not None and rel_ise.da != da_obj:
                    rel_ise.da = da_obj
                    rel_ise.save()

            except Exception as e:
                nb_erreurs += 1
                print(f"✗ Erreur ligne {nb_lignes}: {e}")

        # Enregistrement de l'historique d'import
        ImportHistory.objects.create(
            type_fichier='ISE',
            nom_fichier=fichier.name,
            nb_lignes_traitees=nb_lignes,
            nb_erreurs=nb_erreurs,
            statut='SUCCESS' if nb_erreurs == 0 else ('PARTIAL' if nb_erreurs < nb_lignes else 'ERROR'),
        )
        
        print(f"✓ Import ISE terminé : {nb_lignes} lignes, {nb_erreurs} erreurs")

    except Exception as e:
        ImportHistory.objects.create(
            type_fichier='ISE',
            nom_fichier=fichier.name if hasattr(fichier, 'name') else 'Inconnu',
            nb_lignes_traitees=nb_lignes,
            nb_erreurs=nb_erreurs + 1,
            statut='ERROR',
        )
        print(f"✗ Erreur critique ISE: {e}")
        raise  # Re-lever l'exception pour le debugging