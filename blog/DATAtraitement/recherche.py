from blog.models import ISE, DA, AO, Cde, Appartenir_A_I, Appartenir_A_D, Appartenir_A_A, Commander, Article, Appartenir_P_A
import pandas as pd

def rechercher_ise(code_ise):
    """
    Recherche toutes les informations liées à un code ISE
    """
    try:
        ise_obj = ISE.objects.filter(id_ise=code_ise).first()
        
        if not ise_obj:
            print(f" Aucun ISE trouvé avec le code: {code_ise}")
            return None
        
        relations_ise = Appartenir_A_I.objects.filter(ise=ise_obj).select_related(
            'article', 'article__famille'
        )
        
        if not relations_ise.exists():
            print(f" ISE {code_ise} trouvé mais aucun article associé")
            return None
        
        data = []
        for rel_ise in relations_ise:
            article = rel_ise.article
            
            # Chercher DA
            rel_da = Appartenir_A_D.objects.filter(article=article).select_related('da').first()
            
            # Chercher AO
            rel_ao = Appartenir_A_A.objects.filter(article=article).select_related('ao').first()
            
            # Chercher CMD
            rel_cmd = Commander.objects.filter(article=article).select_related('cde', 'fournisseur').first()
            
            # Chercher Plant
            rel_plant = Appartenir_P_A.objects.filter(article=article).select_related('plant').first()
            
            data.append({
                'Code': article.code_article,
                'Description': article.designation_article,
                'ID ISE': ise_obj.id_ise,
                'Date ISE': rel_ise.date_ise,
                'Qté ISE': rel_ise.quantite_ise,
                'Mnt ISE': rel_ise.montant_ise,
                'DA': rel_da.da.id_DA if rel_da and rel_da.da else 'N/A',
                'Date DA': rel_da.date_DA if rel_da else None,
                'Qté DA': rel_da.quantite_DA if rel_da else None,
                'Mnt DA': rel_da.montant_DA if rel_da else None,
                'AO': rel_ao.ao.id_AO if rel_ao and rel_ao.ao else 'N/A',
                'Date AO': rel_ao.date_AO if rel_ao else None,
                'CMD': rel_cmd.cde.id_Cde if rel_cmd and rel_cmd.cde else 'N/A',
                'Date CMD': rel_cmd.date_Cde if rel_cmd else None,
                'Qté CMD': rel_cmd.quantite_Cde if rel_cmd else None,
                'Mnt CMD': rel_cmd.montant_Cde if rel_cmd else None,
                'Fournisseur': rel_cmd.fournisseur.designation_Fournisseur if rel_cmd and rel_cmd.fournisseur else 'N/A',
                'Plant': rel_plant.plant.code_plant if rel_plant and rel_plant.plant else 'N/A',
                'Désignation Plant': rel_plant.plant.designation_plant if rel_plant and rel_plant.plant else 'N/A'
            })
        
        return pd.DataFrame(data)
        
    except Exception as e:
        print(f" Erreur lors de la recherche ISE: {e}")
        return None


def rechercher_da(code_da):
    """
    Recherche toutes les informations liées à un code DA.
    Crée une ligne pour chaque combinaison Article-ISE.
    """
    try:
        da_obj = DA.objects.filter(id_DA=code_da).first()
        
        if not da_obj:
            print(f" Aucun DA trouvé avec le code: {code_da}")
            return None
        
        relations_da = Appartenir_A_D.objects.filter(da=da_obj).select_related(
            'article', 'article__famille'
        )
        
        if not relations_da.exists():
            print(f" DA {code_da} trouvé mais aucun article associé")
            return None
        
        data = []
        
        for rel_da in relations_da:
            article = rel_da.article
            
            # Récupérer TOUS les ISE pour cet article
            tous_les_ises = list(Appartenir_A_I.objects.filter(article=article).select_related('ise').order_by('id'))
            
            # Chercher AO, CMD, Plant (une seule fois)
            rel_ao = Appartenir_A_A.objects.filter(article=article).select_related('ao').first()
            rel_cmd = Commander.objects.filter(article=article).select_related('cde', 'fournisseur').first()
            rel_plant = Appartenir_P_A.objects.filter(article=article).select_related('plant').first()
            
            # 🟢 CRÉER UNE LIGNE POUR CHAQUE ISE
            if tous_les_ises:
                for rel_ise in tous_les_ises:
                    data.append({
                        'Code': article.code_article,
                        'Description': article.designation_article,
                        
                        'ID ISE': rel_ise.ise.id_ise if rel_ise.ise else 'N/A',
                        'Date ISE': rel_ise.date_ise,
                        'Qté ISE': rel_ise.quantite_ise,
                        'Mnt ISE': rel_ise.montant_ise,
                        
                        'DA': da_obj.id_DA,
                        'Date DA': rel_da.date_DA,
                        'Qté DA': rel_da.quantite_DA,
                        'Mnt DA': rel_da.montant_DA,
                        'AO': rel_ao.ao.id_AO if rel_ao and rel_ao.ao else 'N/A',
                        'Date AO': rel_ao.date_AO if rel_ao else None,
                        'CMD': rel_cmd.cde.id_Cde if rel_cmd and rel_cmd.cde else 'N/A',
                        'Date CMD': rel_cmd.date_Cde if rel_cmd else None,
                        'Qté CMD': rel_cmd.quantite_Cde if rel_cmd else None,
                        'Mnt CMD': rel_cmd.montant_Cde if rel_cmd else None,
                        'Fournisseur': rel_cmd.fournisseur.designation_Fournisseur if rel_cmd and rel_cmd.fournisseur else 'N/A',
                        'Plant': rel_plant.plant.code_plant if rel_plant and rel_plant.plant else 'N/A',
                        'Désignation Plant': rel_plant.plant.designation_plant if rel_plant and rel_plant.plant else 'N/A'
                    })
            else:
                # Si aucun ISE, créer quand même une ligne
                data.append({
                    'Code': article.code_article,
                    'Description': article.designation_article,
                    'ID ISE': 'N/A',
                    'Date ISE': None,
                    'Qté ISE': None,
                    'Mnt ISE': None,
                    'DA': da_obj.id_DA,
                    'Date DA': rel_da.date_DA,
                    'Qté DA': rel_da.quantite_DA,
                    'Mnt DA': rel_da.montant_DA,
                    'AO': rel_ao.ao.id_AO if rel_ao and rel_ao.ao else 'N/A',
                    'Date AO': rel_ao.date_AO if rel_ao else None,
                    'CMD': rel_cmd.cde.id_Cde if rel_cmd and rel_cmd.cde else 'N/A',
                    'Date CMD': rel_cmd.date_Cde if rel_cmd else None,
                    'Qté CMD': rel_cmd.quantite_Cde if rel_cmd else None,
                    'Mnt CMD': rel_cmd.montant_Cde if rel_cmd else None,
                    'Fournisseur': rel_cmd.fournisseur.designation_Fournisseur if rel_cmd and rel_cmd.fournisseur else 'N/A',
                    'Plant': rel_plant.plant.code_plant if rel_plant and rel_plant.plant else 'N/A',
                    'Désignation Plant': rel_plant.plant.designation_plant if rel_plant and rel_plant.plant else 'N/A'
                })
        
        return pd.DataFrame(data)
    except Exception as e:
        print(f" Erreur lors de la recherche DA: {e}")
        return None


def rechercher_ao(code_ao):
    """
    Recherche toutes les informations liées à un code AO
    """
    try:
        ao_obj = AO.objects.filter(id_AO=code_ao).first()
        
        if not ao_obj:
            print(f" Aucun AO trouvé avec le code: {code_ao}")
            return None
        
        relations_ao = Appartenir_A_A.objects.filter(ao=ao_obj).select_related(
            'article', 'article__famille'
        )
        
        if not relations_ao.exists():
            print(f" AO {code_ao} trouvé mais aucun article associé")
            return None
        
        data = []
        for rel_ao in relations_ao:
            article = rel_ao.article
            
            # Chercher ISE
            rel_ise = Appartenir_A_I.objects.filter(article=article).select_related('ise').first()
            
            # Chercher DA
            rel_da = Appartenir_A_D.objects.filter(article=article).select_related('da').first()
            
            # Chercher CMD
            rel_cmd = Commander.objects.filter(article=article).select_related('cde', 'fournisseur').first()
            
            # Chercher Plant
            rel_plant = Appartenir_P_A.objects.filter(article=article).select_related('plant').first()
            
            data.append({
                'Code': article.code_article,
                'Description': article.designation_article,
                'ID ISE': rel_ise.ise.id_ise if rel_ise and rel_ise.ise else 'N/A',
                'Date ISE': rel_ise.date_ise if rel_ise else None,
                'Qté ISE': rel_ise.quantite_ise if rel_ise else None,
                'Mnt ISE': rel_ise.montant_ise if rel_ise else None,
                'DA': rel_da.da.id_DA if rel_da and rel_da.da else 'N/A',
                'Date DA': rel_da.date_DA if rel_da else None,
                'Qté DA': rel_da.quantite_DA if rel_da else None,
                'Mnt DA': rel_da.montant_DA if rel_da else None,
                'AO': ao_obj.id_AO,
                'Date AO': rel_ao.date_AO,
                'CMD': rel_cmd.cde.id_Cde if rel_cmd and rel_cmd.cde else 'N/A',
                'Date CMD': rel_cmd.date_Cde if rel_cmd else None,
                'Qté CMD': rel_cmd.quantite_Cde if rel_cmd else None,
                'Mnt CMD': rel_cmd.montant_Cde if rel_cmd else None,
                'Fournisseur': rel_cmd.fournisseur.designation_Fournisseur if rel_cmd and rel_cmd.fournisseur else 'N/A',
                'Plant': rel_plant.plant.code_plant if rel_plant and rel_plant.plant else 'N/A',
                'Désignation Plant': rel_plant.plant.designation_plant if rel_plant and rel_plant.plant else 'N/A'
            })
        return pd.DataFrame(data)
        
    except Exception as e:
        print(f"❌ Erreur lors de la recherche AO: {e}")
        return None


def rechercher_cmd(code_cmd):
    """
    Recherche CMD avec logique de "CONSOMMATION".
    - 1ère ligne de commande -> prend le 1er ISE et l'enlève de la liste.
    - 2ème ligne de commande -> prend le prochain ISE disponible.
    """
    try:
        cmd_obj = Cde.objects.filter(id_Cde=code_cmd).first()
        
        if not cmd_obj:
            print(f" Aucune commande trouvée avec le code: {code_cmd}")
            return None
        
        # Récupérer toutes les relations Article-CMD pour ce code CMD
        relations_cmd = Commander.objects.filter(cde=cmd_obj).select_related(
            'article', 'article__famille', 'fournisseur'
        )
        
        if not relations_cmd.exists():
            print(f" CMD {code_cmd} trouvée mais aucun article associé")
            return None
        
        data = []
        
        # 🟢 CRÉATION DU STOCK (CACHE)
        # Ce dictionnaire va retenir quels ISE sont encore disponibles pour chaque article
        # Clé = Code Article, Valeur = Liste des objets ISE
        cache_ises = {}

        for rel_cmd in relations_cmd:
            article = rel_cmd.article
            code_art = article.code_article

            # 1. Si on n'a pas encore chargé les ISE pour cet article, on le fait maintenant
            if code_art not in cache_ises:
                # On récupère TOUS les ISE liés à cet article et on les met dans une liste
                tous_les_ises = list(Appartenir_A_I.objects.filter(article=article).select_related('ise').order_by('id'))
                cache_ises[code_art] = tous_les_ises

            # 2. On récupère la liste des ISE restants pour cet article
            ises_disponibles = cache_ises[code_art]
            
            # 3. LOGIQUE DE CONSOMMATION (Le cœur de ta demande)
            rel_ise = None
            if len(ises_disponibles) > 0:
                # .pop(0) prend le PREMIER élément de la liste et le SUPPRIME de la liste
                # Donc au prochain tour de boucle, cet ISE ne sera plus là !
                rel_ise = ises_disponibles.pop(0)
            else:
                # Plus d'ISE disponible (cas où il y a plus de lignes de commande que d'ISE)
                rel_ise = None

            # ---------------------------------------
            # Le reste (DA, AO, Plant) reste classique (.first)
            rel_da = Appartenir_A_D.objects.filter(article=article).select_related('da').first()
            rel_ao = Appartenir_A_A.objects.filter(article=article).select_related('ao').first()
            rel_plant = Appartenir_P_A.objects.filter(article=article).select_related('plant').first()
            
            data.append({
                'Code': article.code_article,
                'Description': article.designation_article,
                
                # Ici on utilise l'ISE qu'on vient de "tirer" de la liste
                'ID ISE': rel_ise.ise.id_ise if rel_ise else 'N/A',
                'Date ISE': rel_ise.date_ise if rel_ise else None,
                'Qté ISE': rel_ise.quantite_ise if rel_ise else None,
                'Mnt ISE': rel_ise.montant_ise if rel_ise else None,
                
                'DA': rel_da.da.id_DA if rel_da and rel_da.da else 'N/A',
                'Date DA': rel_da.date_DA if rel_da else None,
                'Qté DA': rel_da.quantite_DA if rel_da else None,
                'Mnt DA': rel_da.montant_DA if rel_da else None,
                'AO': rel_ao.ao.id_AO if rel_ao and rel_ao.ao else 'N/A',
                'Date AO': rel_ao.date_AO if rel_ao else None,
                'CMD': cmd_obj.id_Cde,
                'Date CMD': rel_cmd.date_Cde,
                'Qté CMD': rel_cmd.quantite_Cde,
                'Mnt CMD': rel_cmd.montant_Cde,
                'Fournisseur': rel_cmd.fournisseur.designation_Fournisseur if rel_cmd.fournisseur else 'N/A',
                'Plant': rel_plant.plant.code_plant if rel_plant and rel_plant.plant else 'N/A',
                'Désignation Plant': rel_plant.plant.designation_plant if rel_plant and rel_plant.plant else 'N/A'
            })
        
        return pd.DataFrame(data)
        
    except Exception as e:
        print(f"❌ Erreur lors de la recherche CMD: {e}")
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