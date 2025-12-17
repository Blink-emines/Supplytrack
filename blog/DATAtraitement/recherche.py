
import pandas as pd
from blog.models import *

def rechercher_ise(code_ise):
    """
    Recherche toutes les informations liées à un code ISE
    """
    try:
        ise_obj = ISE.objects.filter(id_ise=code_ise).first()
        
        if not ise_obj:
            print(f"❌ Aucun ISE trouvé avec le code: {code_ise}")
            return None
        
        # Récupérer toutes les relations Appartenir qui contiennent cet ISE
        relations = Appartenir.objects.filter(ise=ise_obj).select_related(
            'article', 'article__famille', 'ise', 'da', 'ao', 'cde', 'fournisseur'
        )
        
        if not relations.exists():
            print(f"⚠️ ISE {code_ise} trouvé mais aucun article associé")
            return None
        
        data = []
        for rel in relations:
            article = rel.article
            
            # Chercher Plant
            rel_plant = Appartenir_P_A.objects.filter(
                article=article
            ).select_related('plant').first()
            
            data.append({
                'Code': article.code_article,
                'Description': article.designation_article,
                
                # Infos ISE (depuis la table Appartenir)
                'ID ISE': ise_obj.id_ise,
                'Date ISE': rel.date_ise if rel.date_ise else None,
                'Qté ISE': rel.quantite_ise if rel.quantite_ise else None,
                'Mnt ISE': rel.montant_ise if rel.montant_ise else None,
                
                # Infos DA (depuis la table Appartenir)
                'DA': rel.da.id_DA if rel.da else 'N/A',
                'Date DA': rel.date_DA if rel.date_DA else None,
                'Qté DA': rel.quantite_DA if rel.quantite_DA else None,
                'Mnt DA': rel.montant_DA if rel.montant_DA else None,
                
                # Infos AO (depuis la table Appartenir)
                'AO': rel.ao.id_AO if rel.ao else 'N/A',
                'Date AO': rel.date_AO if rel.date_AO else None,
                
                # Infos Commande (depuis la table Appartenir)
                'CMD': rel.cde.id_Cde if rel.cde else 'N/A',
                'Date CMD': rel.date_Cde if rel.date_Cde else None,
                'Qté CMD': rel.quantite_Cde if rel.quantite_Cde else None,
                'Mnt CMD': rel.montant_Cde if rel.montant_Cde else None,
                'Fournisseur': rel.fournisseur.designation_Fournisseur if rel.fournisseur else 'N/A',
                
                # Infos Plant
                'Plant': rel_plant.plant.code_plant if rel_plant and rel_plant.plant else 'N/A',
                'Désignation Plant': rel_plant.plant.designation_plant if rel_plant and rel_plant.plant else 'N/A'
            })
        
        return pd.DataFrame(data)
        
    except Exception as e:
        print(f"💥 Erreur lors de la recherche ISE: {e}")
        import traceback
        traceback.print_exc()
        return None
    
def rechercher_da(code_da):
    """
    Recherche toutes les informations liées à un code DA.
    Crée une ligne pour chaque combinaison Article-ISE.
    """
    try:
        da_obj = DA.objects.filter(id_DA=code_da).first()
        
        if not da_obj:
            print(f"❌ Aucun DA trouvé avec le code: {code_da}")
            return None
        
        # Récupérer toutes les relations Appartenir qui contiennent ce DA
        relations = Appartenir.objects.filter(da=da_obj).select_related(
            'article', 'article__famille', 'ise', 'ao', 'cde', 'fournisseur'
        )
        
        if not relations.exists():
            print(f"⚠️ DA {code_da} trouvé mais aucun article associé")
            return None
        
        data = []
        
        for rel in relations:
            article = rel.article
            
            # Récupérer les infos du plant
            rel_plant = Appartenir_P_A.objects.filter(
                article=article
            ).select_related('plant').first()
            
            data.append({
                'Code': article.code_article,
                'Description': article.designation_article,
                
                # Infos ISE (depuis la table Appartenir)
                'ID ISE': rel.ise.id_ise if rel.ise else 'N/A',
                'Date ISE': rel.date_ise if rel.date_ise else None,
                'Qté ISE': rel.quantite_ise if rel.quantite_ise else None,
                'Mnt ISE': rel.montant_ise if rel.montant_ise else None,
                
                # Infos DA (depuis la table Appartenir)
                'DA': da_obj.id_DA,
                'Date DA': rel.date_DA if rel.date_DA else None,
                'Qté DA': rel.quantite_DA if rel.quantite_DA else None,
                'Mnt DA': rel.montant_DA if rel.montant_DA else None,
                
                # Infos AO (depuis la table Appartenir)
                'AO': rel.ao.id_AO if rel.ao else 'N/A',
                'Date AO': rel.date_AO if rel.date_AO else None,
                
                # Infos Commande (depuis la table Appartenir)
                'CMD': rel.cde.id_Cde if rel.cde else 'N/A',
                'Date CMD': rel.date_Cde if rel.date_Cde else None,
                'Qté CMD': rel.quantite_Cde if rel.quantite_Cde else None,
                'Mnt CMD': rel.montant_Cde if rel.montant_Cde else None,
                'Fournisseur': rel.fournisseur.designation_Fournisseur if rel.fournisseur else 'N/A',
                
                # Infos Plant
                'Plant': rel_plant.plant.code_plant if rel_plant and rel_plant.plant else 'N/A',
                'Désignation Plant': rel_plant.plant.designation_plant if rel_plant and rel_plant.plant else 'N/A'
            })
        
        return pd.DataFrame(data)
        
    except Exception as e:
        print(f"💥 Erreur lors de la recherche DA: {e}")
        import traceback
        traceback.print_exc()
        return None

def rechercher_ao(code_ao):
    """
    Recherche toutes les informations liées à un code AO
    """
    try:
        ao_obj = AO.objects.filter(id_AO=code_ao).first()
        
        if not ao_obj:
            print(f"❌ Aucun AO trouvé avec le code: {code_ao}")
            return None
        
        # Récupérer toutes les relations Appartenir qui contiennent cet AO
        relations = Appartenir.objects.filter(ao=ao_obj).select_related(
            'article', 'article__famille', 'ise', 'da', 'ao', 'cde', 'fournisseur'
        )
        
        if not relations.exists():
            print(f"⚠️ AO {code_ao} trouvé mais aucun article associé")
            return None
        
        data = []
        
        for rel in relations:
            article = rel.article
            
            # Chercher Plant
            rel_plant = Appartenir_P_A.objects.filter(
                article=article
            ).select_related('plant').first()
            
            data.append({
                'Code': article.code_article,
                'Description': article.designation_article,
                
                # Infos ISE (depuis la table Appartenir)
                'ID ISE': rel.ise.id_ise if rel.ise else 'N/A',
                'Date ISE': rel.date_ise if rel.date_ise else None,
                'Qté ISE': rel.quantite_ise if rel.quantite_ise else None,
                'Mnt ISE': rel.montant_ise if rel.montant_ise else None,
                
                # Infos DA (depuis la table Appartenir)
                'DA': rel.da.id_DA if rel.da else 'N/A',
                'Date DA': rel.date_DA if rel.date_DA else None,
                'Qté DA': rel.quantite_DA if rel.quantite_DA else None,
                'Mnt DA': rel.montant_DA if rel.montant_DA else None,
                
                # Infos AO (depuis la table Appartenir)
                'AO': ao_obj.id_AO,
                'Date AO': rel.date_AO if rel.date_AO else None,
                
                # Infos Commande (depuis la table Appartenir)
                'CMD': rel.cde.id_Cde if rel.cde else 'N/A',
                'Date CMD': rel.date_Cde if rel.date_Cde else None,
                'Qté CMD': rel.quantite_Cde if rel.quantite_Cde else None,
                'Mnt CMD': rel.montant_Cde if rel.montant_Cde else None,
                'Fournisseur': rel.fournisseur.designation_Fournisseur if rel.fournisseur else 'N/A',
                
                # Infos Plant
                'Plant': rel_plant.plant.code_plant if rel_plant and rel_plant.plant else 'N/A',
                'Désignation Plant': rel_plant.plant.designation_plant if rel_plant and rel_plant.plant else 'N/A'
            })
        
        return pd.DataFrame(data)
        
    except Exception as e:
        print(f"💥 Erreur lors de la recherche AO: {e}")
        import traceback
        traceback.print_exc()
        return None

def rechercher_cmd(code_cmd):
    """
    Recherche toutes les informations liées à un code CMD.
    Crée une ligne pour chaque combinaison Article-ISE.
    """
    try:
        cmd_obj = Cde.objects.filter(id_Cde=code_cmd).first()
        
        if not cmd_obj:
            print(f"❌ Aucune commande trouvée avec le code: {code_cmd}")
            return None
        
        # Récupérer toutes les relations Appartenir qui contiennent cette commande
        relations = Appartenir.objects.filter(cde=cmd_obj).select_related(
            'article', 'article__famille', 'ise', 'da', 'ao', 'cde', 'fournisseur'
        )
        
        if not relations.exists():
            print(f"⚠️ CMD {code_cmd} trouvée mais aucun article associé")
            return None
        
        data = []
        
        for rel in relations:
            article = rel.article
            
            # Chercher Plant
            rel_plant = Appartenir_P_A.objects.filter(
                article=article
            ).select_related('plant').first()
            
            data.append({
                'Code': article.code_article,
                'Description': article.designation_article,
                
                # Infos ISE (depuis la table Appartenir)
                'ID ISE': rel.ise.id_ise if rel.ise else 'N/A',
                'Date ISE': rel.date_ise if rel.date_ise else None,
                'Qté ISE': rel.quantite_ise if rel.quantite_ise else None,
                'Mnt ISE': rel.montant_ise if rel.montant_ise else None,
                
                # Infos DA (depuis la table Appartenir)
                'DA': rel.da.id_DA if rel.da else 'N/A',
                'Date DA': rel.date_DA if rel.date_DA else None,
                'Qté DA': rel.quantite_DA if rel.quantite_DA else None,
                'Mnt DA': rel.montant_DA if rel.montant_DA else None,
                
                # Infos AO (depuis la table Appartenir)
                'AO': rel.ao.id_AO if rel.ao else 'N/A',
                'Date AO': rel.date_AO if rel.date_AO else None,
                
                # Infos Commande (depuis la table Appartenir)
                'CMD': cmd_obj.id_Cde,
                'Date CMD': rel.date_Cde if rel.date_Cde else None,
                'Qté CMD': rel.quantite_Cde if rel.quantite_Cde else None,
                'Mnt CMD': rel.montant_Cde if rel.montant_Cde else None,
                'Fournisseur': rel.fournisseur.designation_Fournisseur if rel.fournisseur else 'N/A',
                
                # Infos Plant
                'Plant': rel_plant.plant.code_plant if rel_plant and rel_plant.plant else 'N/A',
                'Désignation Plant': rel_plant.plant.designation_plant if rel_plant and rel_plant.plant else 'N/A'
            })
        
        return pd.DataFrame(data)
        
    except Exception as e:
        print(f"💥 Erreur lors de la recherche CMD: {e}")
        import traceback
        traceback.print_exc()
        return None


def rechercher_interactif():
    """
    Mode interactif pour rechercher ISE, DA, AO ou CMD
    """
    print("\n" + "="*150)
    print(" SYSTÈME DE RECHERCHE ISE / DA / AO / CMD")
    print("="*150)
    
    while True:
        print("\n Options:")
        print("  1. Rechercher par code ISE")
        print("  2. Rechercher par code DA")
        print("  3. Rechercher par code AO")
        print("  4. Rechercher par code CMD")
        print("  5. Quitter")
        
        choix = input("\n Votre choix: ").strip()
        
        if choix == "1":
            code_ise = input("\n Entrez le code ISE: ").strip()
            if code_ise:
                df = rechercher_ise(code_ise)
                
                if df is not None and not df.empty:
                    export = input("\n Voulez-vous exporter en Excel? (o/n): ").strip().lower()
                    if export == 'o':
                        nom_fichier = f"ISE_{code_ise}_export.xlsx"
                        df.to_excel(nom_fichier, index=False)
                        print(f" Fichier exporté: {nom_fichier}")
            else:
                print(" Code ISE vide")
                
        elif choix == "2":
            code_da = input("\n Entrez le code DA: ").strip()
            if code_da:
                df = rechercher_da(code_da)
                
                if df is not None and not df.empty:
                    export = input("\n Voulez-vous exporter en Excel? (o/n): ").strip().lower()
                    if export == 'o':
                        nom_fichier = f"DA_{code_da}_export.xlsx"
                        df.to_excel(nom_fichier, index=False)
                        print(f" Fichier exporté: {nom_fichier}")
            else:
                print(" Code DA vide")
                
        elif choix == "3":
            code_ao = input("\n Entrez le code AO: ").strip()
            if code_ao:
                df = rechercher_ao(code_ao)
                
                if df is not None and not df.empty:
                    export = input("\n Voulez-vous exporter en Excel? (o/n): ").strip().lower()
                    if export == 'o':
                        nom_fichier = f"AO_{code_ao}_export.xlsx"
                        df.to_excel(nom_fichier, index=False)
                        print(f" Fichier exporté: {nom_fichier}")
            else:
                print(" Code AO vide")
                
        elif choix == "4":
            code_cmd = input("\n Entrez le code CMD: ").strip()
            if code_cmd:
                df = rechercher_cmd(code_cmd)
                
                if df is not None and not df.empty:
                    export = input("\n Voulez-vous exporter en Excel? (o/n): ").strip().lower()
                    if export == 'o':
                        nom_fichier = f"CMD_{code_cmd}_export.xlsx"
                        df.to_excel(nom_fichier, index=False)
                        print(f" Fichier exporté: {nom_fichier}")
            else:
                print(" Code CMD vide")
                
        elif choix == "5":
            print("\n Au revoir!")
            break
        else:
            print(" Choix invalide")


# Utilisation directe
if __name__ == "__main__":
    # Exemples de recherche directe
    # rechercher_ise("ISE12345")
    # rechercher_da("DA67890")
    # rechercher_ao("AO24680")
    # rechercher_cmd("CMD99999")
    
    # Mode interactif
    rechercher_interactif()