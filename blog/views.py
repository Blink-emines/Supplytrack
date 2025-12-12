from django.shortcuts import render, get_object_or_404
from .DATAtraitement.services import data_service  # Import du singleton
from .models import ISE, AO, DA, Cde,Article, Appartenir_A_I, Appartenir_A_D, Appartenir_A_A, Commander, Appartenir_P_A
from datetime import datetime
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import pandas as pd
from decimal import Decimal
import json
from django.db.models import Sum

from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods

SECURITY_USER = "admin"
SECURITY_CODE = "supply2025"
from django.core.mail import send_mail




def help(request):
    
    context = {
        
    }
    return render(request, 'blog/help.html', context)

def parametres(request):
    """
    View to display the settings/parameters page.
    """
    context = {
        'title': 'Paramètres Généraux',
        # You can add more data here later
    }
    return render(request, 'blog/parametres.html', context)
    
def analyses(request):
    """
    View to display analytics and statistics page with date filtering.
    """
    from django.db.models import Sum, Count, Avg, Q
    from decimal import Decimal
    from datetime import datetime, timedelta
    
    # ========== DATE FILTERING ==========
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    
    # Base querysets
    appartenir_ise_qs = Appartenir_A_I.objects.all()
    appartenir_da_qs = Appartenir_A_D.objects.all()
    commander_qs = Commander.objects.all()
    
    # Apply date filters if provided
    # For ISE - date_ise is directly on Appartenir_A_I model
    if date_from:
        appartenir_ise_qs = appartenir_ise_qs.filter(date_ise__gte=date_from)
        appartenir_da_qs = appartenir_da_qs.filter(date_DA__gte=date_from)
        commander_qs = commander_qs.filter(date_Cde__gte=date_from)
    
    if date_to:
        appartenir_ise_qs = appartenir_ise_qs.filter(date_ise__lte=date_to)
        appartenir_da_qs = appartenir_da_qs.filter(date_DA__lte=date_to)
        commander_qs = commander_qs.filter(date_Cde__lte=date_to)
    
    # Get distinct ISE, DA, AO, Cde counts from filtered querysets
    total_ise = appartenir_ise_qs.values('ise').distinct().count()
    total_da = appartenir_da_qs.values('da').distinct().count()
    
    # For AO - need to get through DA relationship
    da_ids = appartenir_da_qs.values_list('da_id', flat=True).distinct()
    ao_ids = DA.objects.filter(id__in=da_ids).values_list('ao_id', flat=True).distinct()
    total_ao = AO.objects.filter(id__in=ao_ids).count()
    
    # For Commandes
    total_cmd = commander_qs.values('cde').distinct().count()
    
    # ========== MONTANTS TOTAUX PAR ÉTAPE ==========
    montant_total_ise = appartenir_ise_qs.aggregate(
        total=Sum('montant_ise')
    )['total'] or 0
    
    montant_total_da = appartenir_da_qs.aggregate(
        total=Sum('montant_DA')
    )['total'] or 0
    
    montant_total_cmd = commander_qs.aggregate(
        total=Sum('montant_Cde')
    )['total'] or 0
    
    # ========== TAUX DE CONVERSION ==========
    # Pourcentage DA/ISE
    taux_da = int((total_da / total_ise * 100)) if total_ise > 0 else 0
    
    # Pourcentage AO/DA
    taux_ao = int((total_ao / total_da * 100)) if total_da > 0 else 0
    
    # Pourcentage CMD/ISE (taux de réalisation final)
    taux_cmd = 100  # Toutes les commandes sont finalisées
    
    # ========== ÉCART BUDGET ISE vs COMMANDES ==========
    ecart_budget = montant_total_cmd - montant_total_ise
    pourcentage_ecart = (ecart_budget / montant_total_ise * 100) if montant_total_ise > 0 else 0
    
    # ========== TOP FOURNISSEURS ==========
    top_fournisseurs = commander_qs.values(
        'fournisseur__designation_Fournisseur'
    ).annotate(
        nb_commandes=Count('cde', distinct=True),
        nb_codes=Count('id'),
        montant_total=Sum('montant_Cde'),
        montant_moyen=Avg('montant_Cde')
    ).order_by('-montant_total')[:10]
    
    # Calcul du pourcentage pour chaque fournisseur
    for fournisseur in top_fournisseurs:
        if montant_total_cmd > 0:
            fournisseur['pourcentage'] = round(
                (fournisseur['montant_total'] / montant_total_cmd * 100), 1
            )
        else:
            fournisseur['pourcentage'] = 0
    
    # ========== RÉPARTITION PAR PLANT ==========
    repartition_plant = Appartenir_P_A.objects.filter(
        article__in=commander_qs.values_list('article', flat=True)
    ).values(
        'plant__code_plant',
        'plant__designation_plant'
    ).annotate(
        nb_articles=Count('article', distinct=True)
    ).order_by('-nb_articles')[:5]
    
    # ========== RÉPARTITION PAR FAMILLE ==========
    from django.db.models import F
    
    repartition_famille_data = appartenir_ise_qs.values(
        'article__famille__designation_famille'
    ).annotate(
        nb_articles=Count('article', distinct=True),
        montant_ise=Sum(F('montant_ise') * F('quantite_ise'))
    )
    
    # Get commande amounts
    famille_cmd = commander_qs.values(
        'article__famille__designation_famille'
    ).annotate(
        montant_cmd=Sum(F('montant_Cde') * F('quantite_Cde'))
    )
    
    # Merge the data
    famille_dict = {}
    for item in repartition_famille_data:
        famille = item['article__famille__designation_famille'] or 'Non défini'
        famille_dict[famille] = {
            'famille__designation_famille': famille,
            'nb_articles': item['nb_articles'],
            'montant_ise': item['montant_ise'] or 0,
            'montant_cmd': 0
        }
    
    for item in famille_cmd:
        famille = item['article__famille__designation_famille'] or 'Non défini'
        if famille in famille_dict:
            famille_dict[famille]['montant_cmd'] = item['montant_cmd'] or 0
        else:
            famille_dict[famille] = {
                'famille__designation_famille': famille,
                'nb_articles': 0,
                'montant_ise': 0,
                'montant_cmd': item['montant_cmd'] or 0
            }
    
    # Convert to list and sort
    repartition_famille = sorted(
        famille_dict.values(), 
        key=lambda x: x['montant_cmd'], 
        reverse=True
    )[:8]
    
    # ========== DONNÉES POUR GRAPHIQUES (format JSON) ==========
    # Graphique barres : Nombre de documents par étape
    chart_documents = {
        'labels': ['ISE', 'DA', 'AO', 'Commandes'],
        'values': [total_ise, total_da, total_ao, total_cmd]
    }
    
    # Graphique barres : Montants par étape
    chart_montants = {
        'labels': ['ISE', 'DA', 'Commandes'],
        'values': [
            float(montant_total_ise),
            float(montant_total_da),
            float(montant_total_cmd)
        ]
    }
    
    # Graphique ligne : Top 5 fournisseurs
    chart_fournisseurs_labels = [f['fournisseur__designation_Fournisseur'] or 'N/A' 
                                   for f in top_fournisseurs[:5]]
    chart_fournisseurs_values = [float(f['montant_total']) for f in top_fournisseurs[:5]]
    
    context = {
        'current_page': 'analyses',
        
        # Date filter values
        'date_from': date_from or '',
        'date_to': date_to or '',
        
        # Cartes statistiques
        'total_ise': total_ise,
        'total_da': total_da,
        'total_ao': total_ao,
        'total_cmd': total_cmd,
        'taux_da': taux_da,
        'taux_ao': taux_ao,
        'taux_cmd': taux_cmd,
        
        # Montants
        'montant_total_ise': montant_total_ise,
        'montant_total_da': montant_total_da,
        'montant_total_cmd': montant_total_cmd,
        
        # Écart budget
        'ecart_budget': ecart_budget,
        'pourcentage_ecart': pourcentage_ecart,
        
        # Tableaux
        'top_fournisseurs': top_fournisseurs,
        'repartition_plant': repartition_plant,
        'repartition_famille': repartition_famille,
        
        # Données pour graphiques (JSON)
        'chart_documents': chart_documents,
        'chart_montants': chart_montants,
        'chart_fournisseurs_labels': chart_fournisseurs_labels,
        'chart_fournisseurs_values': chart_fournisseurs_values,
    }
    
    return render(request, 'blog/analyses.html', context)
    

@require_http_methods(["POST"])
def update_profile(request):
    """API pour sauvegarder automatiquement les modifications"""
    try:
        data = json.loads(request.body)
        user = request.user
        
        # Mise à jour des champs
        if 'full_name' in data:
            names = data['full_name'].split(' ', 1)
            user.first_name = names[0]
            user.last_name = names[1] if len(names) > 1 else ''
        
        if 'email' in data:
            user.email = data['email']
        
        if 'department' in data and hasattr(user, 'department'):
            user.department = data['department']
        
        user.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Profil mis à jour avec succès'
        })
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=400)


def recherche_view(request):
    context = {}
    
    if request.method == "POST":
        type_choix = request.POST.get('type_doc') # 'ISE', 'DA', etc.
        code_input = request.POST.get('code_input')

        if type_choix and code_input:
            # APPEL CENTRALISÉ : La vue ne sait pas comment on cherche, elle demande juste au service
            df_resultat = data_service.search_info(type_choix, code_input)

            if df_resultat is not None and not df_resultat.empty:
                # Conversion du DataFrame en HTML pour l'affichage
                html_table = df_resultat.to_html(classes='table table-bordered', index=False)
                
                # Calcul des sommes (si les colonnes existent)
                total_ise = df_resultat['Mnt ISE'].sum() if 'Mnt ISE' in df_resultat.columns else 0
                total_da = df_resultat['Mnt DA'].sum() if 'Mnt DA' in df_resultat.columns else 0
                total_cmd = df_resultat['Mnt CMD'].sum() if 'Mnt CMD' in df_resultat.columns else 0

                context = {
                    'resultat': html_table,
                    'totaux': {'ise': total_ise, 'da': total_da, 'cmd': total_cmd},
                    'code_rech': code_input,
                    'type_rech': type_choix
                }
            else:
                context['error'] = f"Aucun résultat trouvé pour {type_choix} : {code_input}"
        else:
            context['error'] = "Veuillez remplir tous les champs."

    return render(request, 'blog/recherche_interface.html', context)
from django.db.models import Sum

from django.db.models import Sum, Max

def dashboard_view(request):
    total_ise = ISE.objects.count()
    total_da = DA.objects.count()
    total_ao = AO.objects.count()
    total_cmd = Cde.objects.count()

    # Récupérer les ISE avec leur date la plus récente, triées par date décroissante
    ises_with_dates = Appartenir_A_I.objects.values('ise').annotate(
        date_max=Max('date_ise')
    ).order_by('-date_max')[:10]
    
    # Extraire les IDs des ISE
    ise_ids = [item['ise'] for item in ises_with_dates]
    
    # Récupérer les objets ISE correspondants
    recent_ises = ISE.objects.filter(id__in=ise_ids)
    
    # Créer un dictionnaire pour garder l'ordre de tri
    ise_dates = {item['ise']: item['date_max'] for item in ises_with_dates}

    demandes_recentes = []

    for ise_obj in recent_ises:
        # Récupérer tous les articles de cette ISE
        articles_ise = Appartenir_A_I.objects.filter(ise=ise_obj).select_related('article')
        
        if not articles_ise.exists():
            continue

        # Montant total par ISE
        montant_total = articles_ise.aggregate(total=Sum('montant_ise'))['total'] or 0

        # Plant (premier article pour affichage)
        first_article = articles_ise.first().article
        rel_plant = Appartenir_P_A.objects.filter(
            article=first_article
        ).select_related('plant').first()

        plant_code = rel_plant.plant.code_plant if rel_plant else "N/A"
        plant_nom = rel_plant.plant.designation_plant if rel_plant else "N/A"
        
        # Utiliser la date maximale de l'ISE
        date_ise = ise_dates.get(ise_obj.id, articles_ise.first().date_ise)

        # 🌟 Détermination du statut
        statut = "En attente"
        
        # Récupérer les IDs des articles de cette ISE
        article_ids = [rel.article.id for rel in articles_ise]
        
        # Vérifier si AU MOINS UN article a une COMMANDE
        has_commande = Commander.objects.filter(
            article_id__in=article_ids
        ).exists()
        
        if has_commande:
            statut = "Validée"
        else:
            # Vérifier si AU MOINS UN article a une DA
            has_da = Appartenir_A_D.objects.filter(
                article_id__in=article_ids
            ).exists()
            
            if has_da:
                statut = "En cours de traitement"

        demandes_recentes.append({
            'id_ise': ise_obj.id_ise,
            'plant_code': plant_code,
            'plant_nom': plant_nom,
            'date': date_ise,
            'montant': montant_total,
            'statut': statut
        })

    # Trier les demandes par date décroissante
    demandes_recentes.sort(key=lambda x: x['date'], reverse=True)

    context = {
        'total_ise': total_ise,
        'total_da': total_da,
        'total_ao': total_ao,
        'total_cmd': total_cmd,
        'demandes_recentes': demandes_recentes,
        'user_name': request.user.get_full_name() if request.user.is_authenticated else 'M. Hajjad',
        'user_role': 'Responsable Approvisionnement',
    }

    return render(request, 'blog/dashboard.html', context)


    
def suivi_view(request):
    context = {}
    
    # Si on appuie sur "Rechercher"
    if request.method == "POST":
        type_choix = request.POST.get('type_doc') # Vient de l'input caché
        code_input = request.POST.get('code_input')

        if type_choix and code_input:
            # Appel au service centralisé (le même qu'avant !)
            df_resultat = data_service.search_info(type_choix, code_input)

            if df_resultat is not None and not df_resultat.empty:
                # On transforme en HTML propre pour l'intégration
                # classes='...' permet d'appliquer du style CSS si besoin
                html_table = df_resultat.to_html(classes='table-result', index=False, border=0)
                
                context = {
                    'resultat': html_table,
                    'code_rech': code_input,
                    'type_rech': type_choix
                }
            else:
                context['error'] = f"Aucune donnée trouvée pour {type_choix} : {code_input}"
    
    return render(request, 'blog/suivi_demandes.html', context)



def detail_flux(request, id_flux, id_ise, id_da, id_ao, id_cmd):
    
    # 0. Récupération optionnelle de l'article pour le titre
    article_obj = Article.objects.filter(code_article=id_flux).first()

    # --- 1. GESTION DE L'ISE ---
    date_ise = None
    montant_ise = 0
    destination_val = '-'
    udm = 'N/A'
    
    if id_ise and id_ise not in ['0', 'N/A']:
        objet_ise = Appartenir_A_I.objects.filter(
            ise__id_ise=id_ise,
            article__code_article=id_flux
        ).select_related('article').first()
        
        if objet_ise:
            date_ise = objet_ise.date_ise 
            montant_ise = objet_ise.montant_ise * objet_ise.quantite_ise
            destination_val = objet_ise.destination
            udm_val = article_obj.udm

    # --- 2. GESTION DE LA DA ---
    date_da = None
    montant_da = 0
    
    if id_da and id_da not in ['0', 'N/A']:
        objet_da = Appartenir_A_D.objects.filter(
            da__id_DA=id_da,
            article__code_article=id_flux
        ).select_related('da').first()
        
        if objet_da:
            date_da = objet_da.date_DA 
            montant_da = objet_da.montant_DA * objet_da.quantite_DA if hasattr(objet_da, 'montant_DA') else 0

    # --- 3. GESTION DE L'AO ---
    date_ao = None
    
    if id_ao and id_ao not in ['0', 'N/A']:
        objet_ao = Appartenir_A_A.objects.filter(
            ao__id_AO=id_ao,
            article__code_article=id_flux
        ).select_related('ao').first()
        
        if objet_ao:
            date_ao = objet_ao.date_AO

    # --- 4. GESTION DE LA COMMANDE (NOUVEAU BLOC) ---
    date_cmd = None
    montant_cmd = 0
    fournisseur_nom = '-'

    if id_cmd and id_cmd not in ['0', 'N/A']:
        objet_cmd = Commander.objects.filter(
            cde__id_Cde=id_cmd,
            article__code_article=id_flux
        ).select_related('cde', 'fournisseur').first()

        if objet_cmd:
            date_cmd = objet_cmd.date_Cde
            montant_cmd = objet_cmd.montant_Cde * objet_cmd.quantite_Cde
            if objet_cmd.fournisseur:
                fournisseur_nom = objet_cmd.fournisseur.designation_Fournisseur
    code_plant = 'N/A'
    nom_plant = 'Non spécifié'

    # On cherche le Plant lié à cet article
    objet_plant = Appartenir_P_A.objects.filter(
        article__code_article=id_flux
    ).select_related('plant').first()

    if objet_plant and objet_plant.plant:
        code_plant = objet_plant.plant.code_plant
        # On vérifie si le champ s'appelle designation_plant ou designation_Plant
        if hasattr(objet_plant.plant, 'designation_plant'):
            nom_plant = objet_plant.plant.designation_plant
        elif hasattr(objet_plant.plant, 'designation_Plant'):
            nom_plant = objet_plant.plant.designation_plant
    article_obj = Article.objects.filter(code_article=id_flux).select_related('famille').first()

    # On prépare la variable SF pour le contexte
    sf_article = 'Non défini'
    if article_obj and article_obj.famille:
        sf_article = article_obj.famille.designation_famille 
    if montant_cmd == 0:
        ecart_total = 0
    else : 
        ecart_total = montant_cmd - montant_ise
    taux_realisation = (montant_cmd / montant_ise) * 100 if montant_ise > 0 else 0
    def calculer_delai_jours(date_debut, date_fin):
        """Calcule le nombre de jours entre deux dates"""
        if not date_debut or not date_fin:
            return 0
        
        try:
            delta = date_fin - date_debut
            return abs(delta.days)
        except:
            return 0  
    delai_ise_da = calculer_delai_jours(date_ise, date_da)
    delai_da_ao = calculer_delai_jours(date_da, date_ao)
    delai_ao_cmd = calculer_delai_jours(date_ao, date_cmd)

    # Délai total (seulement si toutes les dates sont disponibles)
    if date_ise and date_cmd:
        delai_total = calculer_delai_jours(date_ise, date_cmd)
    else:
        delai_total = 0
    # --- 5. CONTEXTE ---
    context = {
        # ISE
        'ise': { 'id_ise': id_ise if id_ise != '0' else 'N/A' },
        'rel_ise': { 'date_ise': date_ise, 'montant_ise': montant_ise },

        # DA
        'rel_da': {
            'da': { 'id_DA': id_da if id_da != '0' else 'N/A' },
            'date_DA': date_da,
            'montant_DA': montant_da
        },

        # AO
        'rel_ao': {
            'ao': { 'id_AO': id_ao if id_ao != '0' else 'N/A' },
            'date_AO': date_ao,
        },

        # Commande (Maintenant dynamique)
        'rel_cmd': {
            'cde': { 'id_Cde': id_cmd if id_cmd != '0' else 'En attente' },
            'date_Cde': date_cmd,
            'montant_Cde': montant_cmd,
            'fournisseur': { 'designation_Fournisseur': fournisseur_nom }
        },

        # Article
        'article': {
            'code_article': id_flux,
            'designation_article': article_obj.designation_article if article_obj else 'Article Inconnu',
            'famille': sf_article,
            'destination': destination_val,
            'udm': udm_val
        },

        'rel_plant': {
            'plant': { 'code_plant': code_plant , 'designation_plant': nom_plant  }
        },
        'ecart_total': ecart_total,
        'taux_realisation': taux_realisation,
        'delai_ise_da': delai_ise_da,
        'delai_da_ao': delai_da_ao,
        'delai_ao_cmd': delai_ao_cmd,
        'delai_total': delai_total,
    }
    
    return render(request, 'blog/detail_flux.html', context)
def import_ise(request):
    if request.method == 'POST' and request.FILES.get('file'):
        try:
            fichier = request.FILES['file']
            
            # APPEL À VOTRE FONCTION EXISTANTE
            data_service.process_ise(fichier)
            
            return JsonResponse({
                'success': True,
                'message': ' Fichier ISE importé avec succès !'
            })
        
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f' Erreur lors de l\'import ISE : {str(e)}'
            }, status=400)
    
    return JsonResponse({'success': False, 'message': 'Aucun fichier fourni'}, status=400)


# ========== IMPORT DA ==========
def import_da(request):
    if request.method == 'POST' and request.FILES.get('file'):
        try:
            fichier = request.FILES['file']
            
            # APPEL À VOTRE FONCTION EXISTANTE
            data_service.process_da(fichier)
            
            return JsonResponse({
                'success': True,
                'message': ' Fichier DA importé avec succès !'
            })
        
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f' Erreur lors de l\'import DA : {str(e)}'
            }, status=400)
    
    return JsonResponse({'success': False, 'message': 'Aucun fichier fourni'}, status=400)


# ========== IMPORT AO ==========
def import_ao(request):
    if request.method == 'POST' and request.FILES.get('file'):
        try:
            fichier = request.FILES['file']
            
            # APPEL À VOTRE FONCTION EXISTANTE
            data_service.process_ao(fichier)
            
            return JsonResponse({
                'success': True,
                'message': ' Fichier AO importé avec succès !'
            })
        
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f' Erreur lors de l\'import AO : {str(e)}'
            }, status=400)
    
    return JsonResponse({'success': False, 'message': 'Aucun fichier fourni'}, status=400)


# ========== IMPORT CMD ==========
def import_cmd(request):
    if request.method == 'POST' and request.FILES.get('file'):
        try:
            fichier = request.FILES['file']
            
            # APPEL À VOTRE FONCTION EXISTANTE
            data_service.process_cde(fichier)
            
            return JsonResponse({
                'success': True,
                'message': ' Fichier CMD importé avec succès !'
            })
        
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f' Erreur lors de l\'import CMD : {str(e)}'
            }, status=400)
    
    return JsonResponse({'success': False, 'message': 'Aucun fichier fourni'}, status=400)


from django.http import JsonResponse
from .models import ImportHistory

def get_import_history(request):
    """API pour récupérer l'historique des imports"""
    imports = ImportHistory.objects.all()[:20]  # 20 derniers imports
    
    data = [{
        'id': imp.id,
        'type_fichier': imp.type_fichier,
        'nom_fichier': imp.nom_fichier,
        'date_import': imp.date_import.strftime('%d/%m/%Y à %H:%M'),
        'nb_lignes_traitees': imp.nb_lignes_traitees,
        'nb_erreurs': imp.nb_erreurs,
        'statut': imp.statut,
       
    } for imp in imports]
    
    return JsonResponse({'success': True, 'data': data})





    
