
import pandas as pd
from .utils import *
from blog.models import *

def process_da_data(fichier):
    nb_lignes = 0
    nb_erreurs = 0
    
    try:
        df_da_1 = pd.read_excel(fichier, sheet_name=0)
        df_da_2 = pd.read_excel(fichier, sheet_name=1)

        df_da_1.drop_duplicates(inplace=True)
        df_da_2.drop_duplicates(inplace=True)  

        df_da = pd.merge(df_da_1, df_da_2, on="DA")
        df_da = df_da.drop(columns=['AO_x','SF_x','Nombre de CODE','Montant DA'])

        # Nettoyage des colonnes décimales
        for c in ['Montant', 'PUMP', 'Qte DA']:
            df_da[c] = clean_decimal(df_da[c])

        # Nettoyage des colonnes texte
        for c in ['DA', 'ID ISE', 'AO_y','Plant', 'Description', 'CODE', 'Déstination', 'Udm', 'SF_y']:
            df_da[c] = clean_text(df_da[c])

        # Nettoyage des dates
        df_da['Date DA'] = clean_date(df_da['Date DA'])

        for _, row in df_da.iterrows():
            try:
                nb_lignes += 1
                
                # Récupération de l'ID DA
                id_da = str(row['DA']).strip()
                id_ao = str(row["AO_y"]).strip() if pd.notna(row["AO_y"]) else None

                # Création/récupération de l'AO si disponible
                ao_obj = None
                if id_ao and id_ao not in ['', 'nan', 'None', 'N/A']:
                    ao_obj, _ = AO.objects.get_or_create(id_AO=id_ao)

                # Création/mise à jour de la DA
                da_obj, created = DA.objects.update_or_create(
                    id_DA=id_da,
                    defaults={"ao": ao_obj}
                )
                
                # Création/récupération de la famille
                famille_obj, _ = Famille.objects.get_or_create(
                    designation_famille=row["SF_y"]
                )
                
                # Récupération/création de l'ISE si disponible
                id_ise = str(row['ID ISE']).strip() if pd.notna(row['ID ISE']) else None
                ise_obj = None
                
                if id_ise and id_ise not in ['', 'nan', 'None', 'N/A']:
                    ise_obj, _ = ISE.objects.get_or_create(
                        id_ise=id_ise,
                        defaults={"da": da_obj}
                    )
                    
                # Création/récupération de l'article
                article_obj, _ = Article.objects.get_or_create(
                    code_article=row["CODE"],
                    defaults={
                        "designation_article": row["Description"],
                        "udm": row["Udm"],
                        "famille": famille_obj
                    }
                )

                # Création/récupération du plant
                plant_obj, _ = Plant.objects.get_or_create(
                    code_plant=row["Plant"],
                    defaults={"designation_plant": "inconnu"}
                )
                
                # Relation Plant-Article
                Appartenir_P_A.objects.get_or_create(
                    plant=plant_obj,
                    article=article_obj
                )
                
                
                # ✅ Création de la relation Article-DA avec tous les champs obligatoires
                Appartenir.objects.filter(
                        article=article_obj,
                        ise=ise_obj
                    ).update(
                        da=da_obj,
                        ao=ao_obj,
                        montant_DA=row["Montant"],
                        date_DA=row['Date DA'],
                        quantite_DA=row["Qte DA"]
                    )

            except Exception as e:
                nb_erreurs += 1
                print(f"✗ Erreur ligne {nb_lignes}: {e}")
                
        # ✅ Enregistrement de l'historique d'import
        ImportHistory.objects.create(
            type_fichier='DA',
            nom_fichier=fichier.name,
            nb_lignes_traitees=nb_lignes,
            nb_erreurs=nb_erreurs,
            statut='SUCCESS' if nb_erreurs == 0 else ('PARTIAL' if nb_erreurs < nb_lignes else 'ERROR'),
        )
        
        print(f"✓ Import DA terminé : {nb_lignes} lignes, {nb_erreurs} erreurs")

    except Exception as e:
        ImportHistory.objects.create(
            type_fichier='DA',
            nom_fichier=fichier.name if hasattr(fichier, 'name') else 'Inconnu',
            nb_lignes_traitees=nb_lignes,
            nb_erreurs=nb_erreurs + 1,
            statut='ERROR',
        )
        print(f"✗ Erreur critique DA: {e}")
        raise  # Re-lever l'exception pour le debugging
