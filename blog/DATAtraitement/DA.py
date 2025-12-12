import pandas as pd
from .utils import * # Assumes clean_decimal, clean_text, clean_date are defined here
from blog.models import Plant, Famille, Article, AO, ISE, DA, Cde, Fournisseur, Appartenir_P_A, Appartenir_A_I, Appartenir_A_D, Appartenir_A_A, Commander, ImportHistory

def process_da_data(fichier):
    nb_lignes = 0
    nb_erreurs = 0
    
    
    try:
        # 1. Read DataFrames from Excel sheets
        df_da_1 = pd.read_excel(fichier, sheet_name=0)
        df_da_2 = pd.read_excel(fichier, sheet_name=1)

        # 2. Clean and Merge DataFrames
        df_da_1.drop_duplicates(inplace=True)
        df_da_2.drop_duplicates(inplace=True) 

        df_da = pd.merge(df_da_1, df_da_2, on="DA", how="inner")
        
        # Dropping unnecessary columns after merge
        df_da = df_da.drop(columns=['AO_x','SF_x','Nombre de CODE','Montant DA'], errors='ignore')

        # 3. Clean Data Types
        for c in ['Montant', 'PUMP', 'Qte DA']:
            df_da[c] = clean_decimal(df_da[c])

        for c in ['DA', 'ID ISE', 'AO_y','Plant', 'Description', 'CODE', 'Déstination', 'Udm', 'SF_y']:
            df_da[c] = clean_text(df_da[c])

        df_da['Date DA'] = clean_date(df_da['Date DA'])

        # 4. Iterate and Save Data
        for _, row in df_da.iterrows():
            try:
                nb_lignes += 1
                
                # Extract and clean key fields
                id_da = str(row['DA']).strip()
                id_ao = str(row["AO_y"]).strip() if pd.notna(row["AO_y"]) else None
                da_date = row['Date DA'] # Store the cleaned date

                # --- 4.1. AO Object Creation ---
                ao_obj = None
                if id_ao and id_ao not in ['', 'nan', 'None', 'N/A']:
                    ao_obj, _ = AO.objects.get_or_create(id_AO=id_ao)

                # --- 4.2. DA Object Creation/Update (FIXED) ---
                # CRITICAL FIX 1: Ensure the DA date is saved on the main DA object.
                da_obj, created = DA.objects.update_or_create(
                    id_DA=id_da,
                    defaults={
                        "ao": ao_obj,
                        "date_DA": da_date # <-- THIS IS THE PRIMARY DATE FIX
                    }
                )
                
                # --- 4.3. Famille Object Creation ---
                famille_obj, _ = Famille.objects.get_or_create(
                    designation_famille=row["SF_y"]
                )

                # --- 4.4. Article Object Creation/Update ---
                article_obj, _ = Article.objects.get_or_create(
                    code_article=row["CODE"],
                    defaults={
                        "designation_article": row["Description"],
                        "udm": row["Udm"],
                        "famille": famille_obj
                    }
                )

                # --- 4.5. Appartenir_A_A (Article - AO) Relationship (FIXED) ---
                if ao_obj:
                    rel_ao, created = Appartenir_A_A.objects.get_or_create(
                        article=article_obj,
                        ao=ao_obj,
                        # Defaults runs ONLY on creation. Uses DA date as AO date fallback.
                        defaults={"date_AO": da_date} 
                    )
                    # CRITICAL FIX 2: If the record already exists (i.e., it had 1900-01-01), force the update.
                    if not created:
                        rel_ao.date_AO = da_date
                        rel_ao.save()
                
                # --- 4.6. Plant Object Creation ---
                plant_obj, _ = Plant.objects.get_or_create(
                    code_plant=row["Plant"],
                    defaults={"designation_plant": "inconnu"}
                )
                
                # --- 4.7. Appartenir_P_A (Plant - Article) Relationship ---
                Appartenir_P_A.objects.get_or_create(
                    plant=plant_obj,
                    article=article_obj
                )
                
                # --- 4.8. Appartenir_A_D (Article - DA) Relationship ---
                # This relationship table is correctly updated with the date as well
                Appartenir_A_D.objects.get_or_create(
                    article=article_obj,
                    da=da_obj,
                    defaults={
                        "montant_DA": row["Montant"],
                        "date_DA": da_date,
                        "quantite_DA": row["Qte DA"],
                        "destination": row["Déstination"]
                    }
                )

            except Exception as e:
                nb_erreurs += 1
                print(f"❌ Error processing row {nb_lignes}: {e}")
                
        # 5. Record Import History
        ImportHistory.objects.create(
            type_fichier='DA',
            nom_fichier=fichier.name,
            nb_lignes_traitees=nb_lignes,
            nb_erreurs=nb_erreurs,
            statut='SUCCESS' if nb_erreurs == 0 else ('PARTIAL' if nb_erreurs < nb_lignes else 'ERROR'),
            
        )
        
        print(f"✅ Import DA terminé : {nb_lignes} lignes, {nb_erreurs} erreurs")

    except Exception as e:
        # 6. Record Critical Import Error
        ImportHistory.objects.create(
            type_fichier='DA',
            nom_fichier=fichier.name if hasattr(fichier, 'name') else 'Inconnu',
            nb_lignes_traitees=nb_lignes,
            nb_erreurs=nb_erreurs + 1,
            statut='ERROR',
            details=f"Erreur critique: {str(e)}"
        )
        print(f"❌ Erreur critique DA: {e}")