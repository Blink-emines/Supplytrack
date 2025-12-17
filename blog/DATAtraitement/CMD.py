import pandas as pd
from .utils import *
from django.utils import timezone
from blog.models import *
def process_cde_data(fichier):
    nb_lignes = 0
    nb_erreurs = 0
    
    
    try:
       
        df_cmd_1 = pd.read_excel(fichier, sheet_name=0)
        df_cmd_2 = pd.read_excel(fichier, sheet_name=1)

        df_cmd_1.drop_duplicates(inplace=True) 
        df_cmd_2.drop_duplicates(inplace=True)  

        df_cmd = pd.merge(df_cmd_1, df_cmd_2, on="Commande")
        df_cmd = df_cmd.drop(columns=['AO_x','Fournissuer','Montant Commande TTC','Nombre de CODE'])

        # Nettoyage des formats
        for c in ['PU Commande', 'Qte Commande', 'Montant Commande']:
            df_cmd[c] = clean_decimal(df_cmd[c])

        for c in ['Commande', 'DA', 'ID ISE','AO_y', 'Fournisseur', 'CODE', 'Description', 'Udm', 'SF','Plant']:
            df_cmd[c] = clean_text(df_cmd[c])

        df_cmd['Date commande'] = clean_date(df_cmd['Date commande'])

        # Boucle sur chaque ligne
        for _, row in df_cmd.iterrows():
            try:
                nb_lignes += 1
                ise_obj = None
                # ✅ NETTOYAGE STRICT
                cmd_value = str(row["Commande"]).strip()
                da_value = str(row["DA"]).strip() if pd.notna(row["DA"]) else None
                ao_value = str(row["AO_y"]).strip() if pd.notna(row["AO_y"]) else None

                # Vérifications
                if not cmd_value or cmd_value in ['NAN', 'NONE', 'N/A', '']:
                    nb_erreurs += 1
                    
                    continue

                # 1. PLANT
                plant_obj, _ = Plant.objects.get_or_create(
                    code_plant=row["Plant"], 
                    defaults={"designation_plant": "inconnu"}
                )

                # 2. FAMILLE
                famille_obj, _ = Famille.objects.get_or_create(
                    designation_famille=row["SF"]
                )
                id_ise = str(row['ID ISE']).strip() if pd.notna(row['ID ISE']) else None

                # Ligne 56-58 - MODIFIER :
                if id_ise and id_ise not in ['', 'nan', 'None', 'N/A']:
                    ise_obj, _ = ISE.objects.get_or_create(id_ise=id_ise)
                # 3. ARTICLE
                article_obj, _ = Article.objects.get_or_create(
                    code_article=row["CODE"],
                    defaults={
                        "designation_article": row["Description"],
                        "udm": row["Udm"],
                        "famille": famille_obj
                    }
                )

                # 4. LIEN PLANT <-> ARTICLE
                Appartenir_P_A.objects.get_or_create(
                    plant=plant_obj, 
                    article=article_obj
                )

                # 5. AO (APPEL D'OFFRE)
                ao_obj = None
                if ao_value and ao_value not in ['', 'NAN', 'NONE', 'N/A']:
                    ao_obj, _ = AO.objects.get_or_create(id_AO=ao_value)

                # 6. DA (DEMANDE D'ACHAT)
                da_obj = None
                if da_value and da_value not in ['', 'NAN', 'NONE', 'N/A']:
                    da_obj, _ = DA.objects.get_or_create(
                        id_DA=da_value, 
                        defaults={"ao": ao_obj}
                    )
                    # Si DA existe déjà sans AO, on l'associe
                    if da_obj.ao is None and ao_obj is not None:
                        da_obj.ao = ao_obj
                        da_obj.save()

                # 7. CDE (COMMANDE)
                cde_obj, _ = Cde.objects.get_or_create(
                    id_Cde=cmd_value,
                    defaults={"ao": ao_obj}
                )

                # 8. FOURNISSEUR
                fournisseur_obj, _ = Fournisseur.objects.get_or_create(
                    designation_Fournisseur=row["Fournisseur"]
                )

                
                Appartenir.objects.filter(
                    article=article_obj,
                    ise=ise_obj,
                    da=da_obj,
                    ao=ao_obj
                ).update(
                    cde=cde_obj,  # ← Virgule manquante ajoutée
                    fournisseur=fournisseur_obj,
                    montant_Cde=row["Montant Commande"],
                    quantite_Cde=row["Qte Commande"],
                    date_Cde=row["Date commande"]
                )
                
                

            except Exception as e:
                nb_erreurs += 1
              

        # ✅ ENREGISTRER L'HISTORIQUE
        ImportHistory.objects.create(
            type_fichier='CMD',
            nom_fichier=fichier.name,
            nb_lignes_traitees=nb_lignes,
            nb_erreurs=nb_erreurs,
            statut='SUCCESS' if nb_erreurs == 0 else ('PARTIAL' if nb_erreurs < nb_lignes else 'ERROR'),
           
        )
        
        print(f"✅ Import CMD terminé : {nb_lignes} lignes, {nb_erreurs} erreurs")

    except Exception as e:
        ImportHistory.objects.create(
            type_fichier='CMD',
            nom_fichier=fichier.name if hasattr(fichier, 'name') else 'Inconnu',
            nb_lignes_traitees=nb_lignes,
            nb_erreurs=nb_erreurs + 1,
            statut='ERROR',
            details=f"Erreur critique: {str(e)}"
        )
        print(f"❌ Erreur critique CMD: {e}")