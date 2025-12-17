from django.db import models
from django.utils import timezone

# 🌿 TABLE PLANT
class Plant(models.Model):
    code_plant = models.CharField(max_length=50, unique=True)
    designation_plant = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.code_plant} - {self.designation_plant}"


# 🏷️ TABLE FAMILLE
class Famille(models.Model):
    code_famille = models.AutoField(primary_key=True)
    designation_famille = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.code_famille} - {self.designation_famille}"


# 📦 TABLE ARTICLE
class Article(models.Model):
    code_article = models.CharField(max_length=50, unique=True)
    designation_article = models.CharField(max_length=200)
    udm = models.CharField(max_length=100)  # Unité de mesure
    famille = models.ForeignKey(Famille, on_delete=models.CASCADE, related_name="articles")

    def __str__(self):
        return f"{self.code_article} - {self.designation_article} - {self.udm} - {self.famille}"


# 🔗 RELATION PLANT - ARTICLE
class Appartenir_P_A(models.Model):
    plant = models.ForeignKey(Plant, on_delete=models.CASCADE)
    article = models.ForeignKey(Article, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('plant', 'article')

    def __str__(self):
        return f"{self.plant} - {self.article}"


# 📄 TABLE AO (Appel d’Offre)
class AO(models.Model):
    id_AO = models.CharField(max_length=50, unique=True, null=True, blank=True)

    def __str__(self):
        return str(self.id_AO)


# 📄 TABLE DA (Demande d’Achat)
class DA(models.Model):
    id_DA = models.CharField(max_length=50, unique=True, null=True, blank=True)
    ao = models.ForeignKey(AO, on_delete=models.CASCADE, related_name="appel_offre" , null=True, blank=True)

    def __str__(self):
        # CORRECTION : On vérifie si self.ao existe avant d'accéder à .id_AO
        ao_display = self.ao.id_AO if self.ao else "Aucun AO"
        return f"DA {self.id_DA} (AO {ao_display})"


# 📄 TABLE ISE
class ISE(models.Model):
    id_ise = models.CharField(max_length=50, unique=True)
    da = models.ForeignKey(DA, on_delete=models.CASCADE, related_name="demande_achat", null=True, blank=True)

    def __str__(self):
        # CORRECTION : On vérifie si self.da existe avant d'accéder à .id_DA
        da_display = self.da.id_DA if self.da else "Aucune DA"
        return f"ISE {self.id_ise} (DA {da_display})"


# 🧾 TABLE COMMANDE (Cde)
class Cde(models.Model):
    id_Cde = models.CharField(max_length=50, unique=True)
    ao = models.ForeignKey(AO, on_delete=models.CASCADE, related_name="appel_offre1", null=True, blank=True)

    def __str__(self):
        # CORRECTION : On vérifie si self.ao existe avant d'accéder à .id_AO
        ao_display = self.ao.id_AO if self.ao else "Aucun AO"
        return f"Cde {self.id_Cde} (AO {ao_display})"


# 🏭 TABLE FOURNISSEUR
class Fournisseur(models.Model):
    code_fournisseur = models.AutoField(primary_key=True)
    designation_Fournisseur = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.code_fournisseur} - {self.designation_Fournisseur}"


# 🔗 RELATION ARTICLE - ISE
class Appartenir(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name="article")
    ise = models.ForeignKey(ISE, on_delete=models.CASCADE, related_name="ISE")
    da = models.ForeignKey(DA, on_delete=models.CASCADE, related_name="demande_achat_ise", 
                          null=True, blank=True)
    ao = models.ForeignKey(AO, on_delete=models.CASCADE, related_name="appel_offre_ise", 
                          null=True, blank=True)
    cde = models.ForeignKey(Cde, on_delete=models.CASCADE, related_name="commande_ise", 
                          null=True, blank=True)
    montant_ise = models.DecimalField(max_digits=10, decimal_places=2)
    date_ise = models.DateField()
    quantite_ise = models.DecimalField(max_digits=10, decimal_places=2, 
                          null=True, blank=True)
    montant_DA = models.DecimalField(max_digits=10, decimal_places=2, 
                          null=True, blank=True)
    date_DA = models.DateField( 
                          null=True, blank=True)
    quantite_DA = models.DecimalField(max_digits=10, decimal_places=2, 
                          null=True, blank=True)
    date_AO = models.DateField(
                          null=True, blank=True)
    fournisseur = models.ForeignKey(Fournisseur, on_delete=models.CASCADE, related_name="fournisseur", 
                          null=True, blank=True)
    montant_Cde = models.DecimalField(max_digits=10, decimal_places=2, 
                          null=True, blank=True)
    date_Cde = models.DateField(null=True, blank=True)
    quantite_Cde = models.DecimalField(max_digits=10, decimal_places=2, 
                          null=True, blank=True)
    destination = models.CharField(max_length=200)
    
    def __str__(self):
        return f"{self.article} - ISE {self.ise} ({self.date_ise}) - {self.montant_ise} - {self.quantite_ise} - {self.destination}"



class ImportHistory(models.Model):
    TYPE_CHOICES = [
        ('ISE', 'ISE'),
        ('DA', 'DA'),
        ('AO', 'AO'),
        ('CMD', 'Commande'),
    ]
    
    STATUT_CHOICES = [
        ('SUCCESS', 'Succès'),
        ('PARTIAL', 'Partiel'),
        ('ERROR', 'Erreur'),
    ]
    
    type_fichier = models.CharField(max_length=10, choices=TYPE_CHOICES)
    nom_fichier = models.CharField(max_length=255)
    date_import = models.DateTimeField(default=timezone.now)
    nb_lignes_traitees = models.IntegerField(default=0)
    nb_erreurs = models.IntegerField(default=0)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='SUCCESS')
    
    
    class Meta:
        ordering = ['-date_import']
        verbose_name = "Historique d'import"
        verbose_name_plural = "Historiques d'imports"
    
    def __str__(self):
        return f"{self.type_fichier} - {self.date_import.strftime('%d/%m/%Y %H:%M')}"