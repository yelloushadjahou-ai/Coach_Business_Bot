"""
Coach Business Pro — Bot Telegram
Pack : Mon Carnet de Bord Business
"""

import os
import logging
import json
import urllib.request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters, ContextTypes
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TOKEN = os.environ.get("BOT_TOKEN", "REMPLACE_PAR_TON_TOKEN")
ANTHROPIC_KEY = os.environ.get("ANTHROPIC_API_KEY", "")

# ─────────────────────────────────────────────────────────────────
# DONNEES PAR PAYS
# ─────────────────────────────────────────────────────────────────
PAYS = {
    "benin": {
        "nom": "Bénin 🇧🇯",
        "fiscal_id": "IFU (Identifiant Fiscal Unique)",
        "registre": "RCCM (Registre du Commerce et du Crédit Mobilier)",
        "impots": "Direction Générale des Impôts (DGI)",
        "cfe": "Centre de Formalités des Entreprises (CFE)",
        "micro": "Régime de la microentreprise (CA sous le seuil DGI)",
        "patente": "La patente est due annuellement avant le 31 mars.",
        "site": "impots.bj",
        "creation": (
            "Au Bénin, pour créer ton entreprise :\n"
            "1. Rends-toi au CFE de Cotonou ou d'une ville proche\n"
            "2. Fournis une pièce d'identité + photos d'identité\n"
            "3. Obtiens ton IFU auprès de la DGI\n"
            "4. Immatricule-toi au RCCM si tu crées une société\n"
            "5. Délai moyen : 72h pour une entreprise individuelle"
        ),
    },
    "cote_ivoire": {
        "nom": "Côte d'Ivoire 🇨🇮",
        "fiscal_id": "Compte Contribuable (DGI-CI)",
        "registre": "RCCM",
        "impots": "Direction Générale des Impôts (DGI-CI)",
        "cfe": "CEPICI (Centre de Promotion des Investissements)",
        "micro": "Régime de l'Auto-Entrepreneur (CA < 50 millions FCFA)",
        "patente": "La contribution des patentes est annuelle.",
        "site": "dgi.gouv.ci",
        "creation": (
            "En Côte d'Ivoire :\n"
            "1. Passe par le guichet unique du CEPICI\n"
            "2. Création possible en ligne sur cepici.gouv.ci\n"
            "3. Délai moyen : 24h à 48h\n"
            "4. Coût : à partir de 0 FCFA pour l'auto-entrepreneur\n"
            "5. Obtiens ton compte contribuable à la DGI"
        ),
    },
    "senegal": {
        "nom": "Sénégal 🇸🇳",
        "fiscal_id": "NINEA (Numéro d'Identification National des Entreprises)",
        "registre": "RCCM",
        "impots": "Direction Générale des Impôts et Domaines (DGID)",
        "cfe": "Agence de Promotion des Investissements (APIX)",
        "micro": "Statut de l'Entrepreneur Individuel (EI)",
        "patente": "La Contribution Économique Locale (CEL) remplace la patente.",
        "site": "impotsetdomaines.gouv.sn",
        "creation": (
            "Au Sénégal :\n"
            "1. Passe par le BACE ou l'APIX\n"
            "2. Obtiens ton NINEA à la DGID\n"
            "3. Immatricule-toi au RCCM si nécessaire\n"
            "4. Délai moyen : 24h à 72h\n"
            "5. Plateforme en ligne : monespace.apix.sn"
        ),
    },
    "burkina": {
        "nom": "Burkina Faso 🇧🇫",
        "fiscal_id": "NIF (Numéro d'Identification Fiscale)",
        "registre": "RCCM",
        "impots": "Direction Générale des Impôts (DGI Burkina)",
        "cfe": "CEFORE (Centre de Facilitation des Actes de Faire des Entreprises)",
        "micro": "Taxe Professionnelle Unique (TPU) pour petites entreprises",
        "patente": "La Taxe Professionnelle Unique (TPU) couvre plusieurs obligations.",
        "site": "dgi.gov.bf",
        "creation": (
            "Au Burkina Faso :\n"
            "1. Rends-toi au CEFORE le plus proche\n"
            "2. Fournis pièce d'identité + formulaire\n"
            "3. Obtiens ton NIF à la DGI\n"
            "4. Délai moyen : 72h\n"
            "5. Coût : autour de 45 000 FCFA pour une SARL"
        ),
    },
    "togo": {
        "nom": "Togo 🇹🇬",
        "fiscal_id": "NIF (Numéro d'Identification Fiscale)",
        "registre": "RCCM",
        "impots": "Office Togolais des Recettes (OTR)",
        "cfe": "Agence de Promotion des Investissements (API-ZF)",
        "micro": "Régime simplifié pour petites entreprises (OTR)",
        "patente": "La contribution des patentes est due annuellement.",
        "site": "otr.tg",
        "creation": (
            "Au Togo :\n"
            "1. Passe par le guichet unique de l'API-ZF à Lomé\n"
            "2. Création possible en ligne sur api.tg\n"
            "3. Obtiens ton NIF à l'OTR\n"
            "4. Délai moyen : 24h\n"
            "5. Coût réduit pour les petites entreprises"
        ),
    },
    "autre": {
        "nom": "Autre pays 🌍",
        "fiscal_id": "Numéro d'identification fiscale de ton pays",
        "registre": "Registre du Commerce de ton pays",
        "impots": "Administration fiscale de ton pays",
        "cfe": "Guichet de création d'entreprise de ton pays",
        "micro": "Régime des petites entreprises de ton pays",
        "patente": "Renseigne-toi auprès de ton administration fiscale locale.",
        "site": "Voir site administration fiscale de ton pays",
        "creation": (
            "Pour créer ton entreprise :\n"
            "1. Renseigne-toi au guichet unique de création d'entreprise\n"
            "2. Obtiens ton numéro fiscal auprès de l'administration\n"
            "3. Immatricule-toi au registre du commerce si nécessaire\n"
            "4. Consulte un comptable ou juriste local pour les détails"
        ),
    },
}

# ─────────────────────────────────────────────────────────────────
# CONTENU COMPTABILITE
# ─────────────────────────────────────────────────────────────────
COMPTA = {
    "benefice": (
        "📊 *Calculer ton bénéfice net*\n\n"
        "*Bénéfice net = Chiffre d'affaires − Toutes tes charges*\n\n"
        "Tes charges incluent :\n"
        "• Achat marchandises / matières premières\n"
        "• Transport et livraison\n"
        "• Loyer ou location\n"
        "• Téléphone et internet\n"
        "• Emballages et fournitures\n"
        "• Ton propre salaire (oui, tu dois te payer !)\n\n"
        "💡 *Coach :* Si tu ne notes pas tes dépenses, tu travailles "
        "peut-être à perte sans le savoir. Remplis ton budget mensuel "
        "dans ton Carnet de Bord chaque fin de mois — 15 minutes suffisent."
    ),
    "charges": (
        "🏗️ *Charges fixes vs charges variables*\n\n"
        "*Charges fixes* — tu les paies même si tu ne vends rien :\n"
        "Loyer, abonnement téléphone, internet...\n\n"
        "*Charges variables* — elles augmentent avec tes ventes :\n"
        "Matières premières, emballages, transport...\n\n"
        "💡 *Coach :* Pour fixer ton prix de vente, inclus toujours une part "
        "de tes charges fixes dans chaque produit. Utilise ton calculateur "
        "de prix pour faire ce calcul automatiquement."
    ),
    "seuil": (
        "📉 *Ton seuil de rentabilité*\n\n"
        "C'est le montant minimum que tu dois vendre pour ne pas perdre d'argent.\n\n"
        "*Exemple simple :*\n"
        "• Loyer mensuel : 30 000 FCFA\n"
        "• Un article : coût 2 000 FCFA, vendu 5 000 FCFA\n"
        "• Marge par article : 3 000 FCFA\n"
        "• Il te faut vendre *10 articles* minimum pour couvrir le loyer\n\n"
        "💡 *Coach :* Connais ton seuil de rentabilité. En dessous, tu perds de l'argent."
    ),
    "tresorerie": (
        "💵 *Gérer ta trésorerie*\n\n"
        "La trésorerie c'est l'argent réellement disponible — pas ton chiffre d'affaires.\n\n"
        "❌ *Erreurs fréquentes :*\n"
        "• Confondre CA et bénéfice\n"
        "• Ne pas prévoir les périodes creuses\n"
        "• Mélanger argent personnel et argent du business\n\n"
        "✅ *Bonne pratique :* Ouvre un Mobile Money dédié à ton business. "
        "Ce qui entre est pour le business, ce que tu te verses est ton salaire.\n\n"
        "💡 *Coach :* La règle des 3 comptes — Opérations / Épargne business (10% de chaque vente) / Ton salaire."
    ),
    "stock": (
        "📦 *Gérer ton stock*\n\n"
        "Un stock mal géré = argent immobilisé ou ventes perdues.\n\n"
        "*Méthode simple :*\n"
        "• Note ton stock initial\n"
        "• Note chaque achat\n"
        "• Note chaque vente\n"
        "• Inventaire une fois par mois\n\n"
        "*Stock final = Stock initial + Achats − Ventes*\n\n"
        "💡 *Coach :* Si un produit ne se vend pas depuis 2 mois, fais une promo "
        "pour récupérer ta mise plutôt qu'immobiliser ton argent."
    ),
}

# ─────────────────────────────────────────────────────────────────
# CONTENU PRIX
# ─────────────────────────────────────────────────────────────────
PRIX = {
    "horaire": (
        "⏱️ *Calculer ton tarif horaire*\n\n"
        "*Étape 1 — Ton coût de vie mensuel :*\n"
        "Loyer + nourriture + transport + téléphone + autres\n\n"
        "*Étape 2 — Tes charges professionnelles :*\n"
        "Matériel + déplacements + imprévus\n\n"
        "*Étape 3 — Tes heures travaillées :*\n"
        "Ex : 6h/jour × 22 jours = 132h/mois\n\n"
        "*Tarif minimum = (Coût vie + Charges pro) ÷ Heures*\n\n"
        "💡 *Coach :* Ce tarif minimum n'est pas ton prix de vente — "
        "ajoute au moins 30% de bénéfice par-dessus pour pouvoir te développer."
    ),
    "revient": (
        "🧮 *Calculer ton coût de revient*\n\n"
        "*Pour un commerçant :*\n"
        "Prix d'achat + Transport + Emballage + Part loyer\n\n"
        "*Pour un artisan / créateur :*\n"
        "Matières premières + Temps de travail + Amortissement matériel + Part loyer\n\n"
        "💡 *Coach :* Beaucoup oublient d'inclure leur temps. Ton temps a une valeur — "
        "inclus-le toujours dans ton coût de revient."
    ),
    "marge": (
        "📈 *Quelle marge viser ?*\n\n"
        "*Marge (%) = (Prix vente − Coût revient) ÷ Prix vente × 100*\n\n"
        "*Repères par secteur :*\n"
        "• Commerce de détail : 30 à 50% minimum\n"
        "• Artisanat / création : 50 à 70%\n"
        "• Services : 60 à 80%\n"
        "• Produits alimentaires : 40 à 60%\n\n"
        "💡 *Coach :* Si ta marge est sous 30%, tu travailles dur pour peu. "
        "Revois soit tes coûts, soit ton prix de vente."
    ),
    "promo": (
        "🏷️ *Faire des promos intelligemment*\n\n"
        "Avant de faire une promo, demande-toi :\n"
        "• Est-ce que je couvre encore mon coût de revient ?\n"
        "• Combien d'unités dois-je vendre pour compenser ?\n"
        "• La promo attire-t-elle de nouveaux clients ?\n\n"
        "*Règle d'or : ne descends jamais sous coût de revient + 10%*\n\n"
        "💡 *Coach :* Préfère offrir de la valeur ajoutée "
        "(bonus, livraison offerte) plutôt que baisser le prix. "
        "Ça préserve ton image de qualité."
    ),
    "negociation": (
        "🤝 *Tenir face à la négociation*\n\n"
        "❌ *À éviter :* baisser le prix immédiatement sans contrepartie\n\n"
        "✅ *Ce que tu peux faire :*\n"
        "• Proposer un lot (2 pour le prix de 1,8)\n"
        "• Offrir un petit bonus (échantillon, livraison)\n"
        "• Proposer un paiement échelonné\n"
        "• Tenir ton prix en expliquant la valeur\n\n"
        "💡 *Coach :* Si un client refuse ton prix, il n'est peut-être pas "
        "ton client cible. Ne te dévalorise pas — chaque réduction affecte ta rentabilité."
    ),
}

# ─────────────────────────────────────────────────────────────────
# CONTENU GUIDE
# ─────────────────────────────────────────────────────────────────
GUIDE = {
    "debut": (
        "🚀 *Par où commencer avec ton guide ?*\n\n"
        "*Semaine 1 — Partie 1 (30 min)*\n"
        "Remplis ta présentation business, client idéal, image de marque. Une seule fois.\n\n"
        "*Semaine 2 — Partie 2 (1h)*\n"
        "Liste tous tes produits avec coûts et prix. Utilise le calculateur de prix.\n\n"
        "*Fin du 1er mois — Parties 3 & 4*\n"
        "Fixe tes objectifs et fais ton premier bilan mensuel.\n\n"
        "💡 *Coach :* Un guide rempli à 70% vaut mieux qu'un guide parfait jamais commencé."
    ),
    "parties": (
        "📚 *Les 4 parties de ton guide*\n\n"
        "🟠 *Partie 1 — Connaître son business*\n"
        "Présentation, infos légales, client idéal, image de marque\n"
        "_Remplis une fois, mets à jour si quelque chose change_\n\n"
        "🟢 *Partie 2 — Gérer ses finances*\n"
        "Liste produits/prix, budget mensuel (12 mois)\n"
        "_15 minutes par mois en fin de mois_\n\n"
        "🟣 *Partie 3 — Développer son business*\n"
        "Objectifs annuels, calendrier contenu, fiches clients\n"
        "_À utiliser en début de mois pour planifier_\n\n"
        "🔵 *Partie 4 — Faire le bilan*\n"
        "Bilan mensuel et annuel\n"
        "_30 minutes en fin de mois_"
    ),
    "faq": (
        "❓ *Questions fréquentes*\n\n"
        "*Je n'ai pas tous les chiffres ?*\n"
        "Commence avec ce que tu as. Tu complèteras au fur et à mesure.\n\n"
        "*Le guide me semble long.*\n"
        "Concentre-toi uniquement sur la Partie 2 (budget mensuel) pour commencer.\n\n"
        "*Je dois l'imprimer ?*\n"
        "Non, Google Docs sur téléphone fonctionne très bien. "
        "Mais beaucoup préfèrent l'imprimer — les deux marchent.\n\n"
        "*J'ai perdu le fichier.*\n"
        "Re-télécharge ton achat directement sur la boutique — "
        "tes achats sont sauvegardés sur ton compte."
    ),
    "astuce": (
        "💡 *Astuce du jour — La règle des 3 comptes*\n\n"
        "📱 *Compte 1 — Opérations*\n"
        "Pour recevoir les paiements et payer les fournisseurs\n\n"
        "💰 *Compte 2 — Épargne business*\n"
        "Mets 10% de chaque vente de côté pour les imprévus\n\n"
        "👤 *Compte 3 — Ton salaire*\n"
        "Verse-toi un salaire fixe — ne pioche pas dans les fonds du business\n\n"
        "💡 Mélanger argent personnel et business est la première cause d'échec financier chez les petits entrepreneurs."
    ),
    "motivation": (
        "🔥 *Un mot de ton coach*\n\n"
        "Chaque grand business a commencé exactement là où tu es maintenant.\n\n"
        "La différence entre ceux qui réussissent et les autres, "
        "ce n'est pas le talent ou la chance — c'est la *régularité*.\n\n"
        "Ceux qui notent leurs chiffres, font leur bilan chaque mois, "
        "ajustent leur stratégie... ils avancent.\n\n"
        "Tu as investi dans ce guide parce que tu prends ton business au sérieux. "
        "C'est déjà un grand pas en avant.\n\n"
        "*Continue. Un mois à la fois. Un objectif à la fois.* 💪"
    ),
}

# ─────────────────────────────────────────────────────────────────
# CLAVIERS
# ─────────────────────────────────────────────────────────────────
def kb_main():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📊 Comptabilité", callback_data="menu_compta"),
         InlineKeyboardButton("💰 Prix & Marges", callback_data="menu_prix")],
        [InlineKeyboardButton("⚖️ Légal & Fiscal", callback_data="menu_legal"),
         InlineKeyboardButton("📖 Aide Guide", callback_data="menu_guide")],
        [InlineKeyboardButton("🔔 Rappels mensuels", callback_data="menu_rappels")],
        [InlineKeyboardButton("🤖 Poser une question au coach", callback_data="menu_ia")],
    ])

def kb_back():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⬅️ Retour au menu", callback_data="menu_main")]
    ])

def kb_compta():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📈 Calculer mon bénéfice", callback_data="compta_benefice")],
        [InlineKeyboardButton("🏗️ Charges fixes vs variables", callback_data="compta_charges")],
        [InlineKeyboardButton("📉 Seuil de rentabilité", callback_data="compta_seuil")],
        [InlineKeyboardButton("💵 Gérer ma trésorerie", callback_data="compta_tresorerie")],
        [InlineKeyboardButton("📦 Gérer mon stock", callback_data="compta_stock")],
        [InlineKeyboardButton("⬅️ Retour au menu", callback_data="menu_main")],
    ])

def kb_prix():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⏱️ Mon tarif horaire", callback_data="prix_horaire")],
        [InlineKeyboardButton("🧮 Mon coût de revient", callback_data="prix_revient")],
        [InlineKeyboardButton("📈 Quelle marge viser ?", callback_data="prix_marge")],
        [InlineKeyboardButton("🏷️ Faire des promos", callback_data="prix_promo")],
        [InlineKeyboardButton("🤝 Tenir face à la négociation", callback_data="prix_negociation")],
        [InlineKeyboardButton("⬅️ Retour au menu", callback_data="menu_main")],
    ])

def kb_legal():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🇧🇯 Bénin", callback_data="legal_benin"),
         InlineKeyboardButton("🇨🇮 Côte d'Ivoire", callback_data="legal_cote_ivoire")],
        [InlineKeyboardButton("🇸🇳 Sénégal", callback_data="legal_senegal"),
         InlineKeyboardButton("🇧🇫 Burkina Faso", callback_data="legal_burkina")],
        [InlineKeyboardButton("🇹🇬 Togo", callback_data="legal_togo"),
         InlineKeyboardButton("🌍 Autre pays", callback_data="legal_autre")],
        [InlineKeyboardButton("⬅️ Retour au menu", callback_data="menu_main")],
    ])

def kb_legal_detail(pays_key):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🪪 Numéro fiscal", callback_data=f"ld_{pays_key}_fiscal")],
        [InlineKeyboardButton("📋 Créer mon entreprise", callback_data=f"ld_{pays_key}_creation")],
        [InlineKeyboardButton("💸 Mes obligations fiscales", callback_data=f"ld_{pays_key}_impots")],
        [InlineKeyboardButton("🔙 Changer de pays", callback_data="menu_legal")],
        [InlineKeyboardButton("⬅️ Retour au menu", callback_data="menu_main")],
    ])

def kb_guide():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🚀 Par où commencer ?", callback_data="guide_debut")],
        [InlineKeyboardButton("📚 Les 4 parties", callback_data="guide_parties")],
        [InlineKeyboardButton("❓ Questions fréquentes", callback_data="guide_faq")],
        [InlineKeyboardButton("💡 Astuce du jour", callback_data="guide_astuce")],
        [InlineKeyboardButton("🔥 Motivation du coach", callback_data="guide_motivation")],
        [InlineKeyboardButton("⬅️ Retour au menu", callback_data="menu_main")],
    ])

def kb_rappels(actifs):
    label = "🔕 Désactiver les rappels" if actifs else "🔔 Activer les rappels"
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(label, callback_data="rappel_toggle")],
        [InlineKeyboardButton("⬅️ Retour au menu", callback_data="menu_main")],
    ])

# ─────────────────────────────────────────────────────────────────
# HANDLERS
# ─────────────────────────────────────────────────────────────────
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prenom = update.effective_user.first_name or "entrepreneur"
    if "rappels_actifs" not in context.user_data:
        context.user_data["rappels_actifs"] = False
    texte = (
        f"👋 Bonjour *{prenom}* !\n\n"
        "Je suis ton *Coach Business Pro* — l'assistant inclus avec ton pack "
        "*Mon Carnet de Bord Business*.\n\n"
        "Je suis là pour t'aider à :\n"
        "• Mieux comprendre ta comptabilité\n"
        "• Fixer tes prix correctement\n"
        "• Naviguer les démarches légales (5 pays)\n"
        "• Tirer le meilleur de ton guide\n\n"
        "Par quoi veux-tu commencer ? 👇"
    )
    await update.message.reply_text(texte, parse_mode="Markdown", reply_markup=kb_main())

async def menu_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Que veux-tu explorer ? 👇", reply_markup=kb_main())

async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    d = q.data
 
    # Menu principal
    if d == "menu_main":
        await q.edit_message_text("Que veux-tu explorer ? 👇", reply_markup=kb_main())
 
    # Comptabilité
    elif d == "menu_compta":
        await q.edit_message_text("📊 *Comptabilité*\n\nChoisis un sujet :",
                                   parse_mode="Markdown", reply_markup=kb_compta())
    elif d.startswith("compta_"):
        key = d[7:]
        await q.edit_message_text(COMPTA.get(key, "Sujet non trouvé."),
                                   parse_mode="Markdown", reply_markup=kb_back())
 
    # Prix
    elif d == "menu_prix":
        await q.edit_message_text("💰 *Prix & Marges*\n\nChoisis un sujet :",
                                   parse_mode="Markdown", reply_markup=kb_prix())
    elif d.startswith("prix_"):
        key = d[5:]
        await q.edit_message_text(PRIX.get(key, "Sujet non trouvé."),
                                   parse_mode="Markdown", reply_markup=kb_back())
 
    # Légal — sélection pays
    elif d == "menu_legal":
        await q.edit_message_text(
            "⚖️ *Légal & Fiscal*\n\nSélectionne ton pays pour des informations adaptées :",
            parse_mode="Markdown", reply_markup=kb_legal())
 
    elif d.startswith("legal_") and not d.startswith("ld_"):
        pays_key = d[6:]
        p = PAYS.get(pays_key, PAYS["autre"])
        context.user_data["pays"] = pays_key
        await q.edit_message_text(
            f"⚖️ *Légal & Fiscal — {p['nom']}*\n\nQue veux-tu savoir ?",
            parse_mode="Markdown", reply_markup=kb_legal_detail(pays_key))
 
    # Légal — détail
    elif d.startswith("ld_"):
        parts = d[3:].rsplit("_", 1)
        pays_key = parts[0]
        sujet = parts[1] if len(parts) > 1 else ""
        p = PAYS.get(pays_key, PAYS["autre"])
 
        if sujet == "fiscal":
            texte = (
                f"🪪 *Numéro fiscal — {p['nom']}*\n\n"
                f"Dans ton pays, le numéro fiscal s'appelle :\n"
                f"*{p['fiscal_id']}*\n\n"
                f"Il est obligatoire pour :\n"
                f"• Ouvrir un compte bancaire professionnel\n"
                f"• Émettre des factures légales\n"
                f"• Passer des marchés avec des entreprises ou l'État\n\n"
                f"📍 Où l'obtenir : {p['impots']}\n"
                f"🌐 Site : {p['site']}\n\n"
                f"💡 *Coach :* Être en règle te protège et te donne accès à de meilleurs marchés."
            )
        elif sujet == "creation":
            texte = (
                f"📋 *Créer ton entreprise — {p['nom']}*\n\n"
                f"{p['creation']}\n\n"
                f"🏢 *Structure d'accueil :* {p['cfe']}\n"
                f"📋 *Registre :* {p['registre']}\n\n"
                f"💡 *Coach :* Commence par une entreprise individuelle — "
                f"plus simple et moins coûteux. Tu évolueras quand ton business grandira."
            )
        elif sujet == "impots":
            texte = (
                f"💸 *Obligations fiscales — {p['nom']}*\n\n"
                f"*Administration :* {p['impots']}\n\n"
                f"*Régime recommandé pour démarrer :*\n{p['micro']}\n\n"
                f"*Patente :* {p['patente']}\n\n"
                f"🌐 Site officiel : {p['site']}\n\n"
                f"⚠️ Ces informations sont générales. Consulte un comptable "
                f"ou l'administration fiscale pour ta situation précise.\n\n"
                f"💡 *Coach :* Être en règle dès le début t'évite de gros problèmes plus tard."
            )
    else:
        texte = "Information non disponible."
 
        await q.edit_message_text(texte, parse_mode="Markdown",
                                   reply_markup=kb_legal_detail(pays_key))
 
    # Guide
    elif d == "menu_guide":
        await q.edit_message_text("📖 *Aide — Mon Carnet de Bord Business*\n\nChoisis un sujet :",
                                   parse_mode="Markdown", reply_markup=kb_guide())
    elif d.startswith("guide_"):
        key = d[6:]
        await q.edit_message_text(GUIDE.get(key, "Sujet non trouvé."),
                                   parse_mode="Markdown", reply_markup=kb_back())
 
    # Rappels
    elif d == "menu_rappels":
        actifs = context.user_data.get("rappels_actifs", False)
        statut = "✅ activés" if actifs else "❌ désactivés"
        texte = (
            f"🔔 *Rappels mensuels*\n\n"
            f"Statut : rappels *{statut}*\n\n"
            f"Quand actifs, tu reçois :\n"
            f"• Le 25 du mois : rappel budget mensuel\n"
            f"• Le 28 du mois : rappel bilan mensuel\n"
            f"• Le 1er du mois : rappel objectifs\n\n"
            f"Ces rappels font une grande différence sur la durée ! 💪"
        )
        await q.edit_message_text(texte, parse_mode="Markdown", reply_markup=kb_rappels(actifs))
 
    # IA — question libre
    elif d == "menu_ia":
        context.user_data["mode_ia"] = True
        await q.edit_message_text(
            "🤖 *Coach IA — Question libre*\n\n"
            "Pose-moi n'importe quelle question sur :\n"
            "• Ta comptabilité et tes finances\n"
            "• La fixation de tes prix\n"
            "• Les démarches légales de ton pays\n"
            "• L'utilisation de ton guide\n"
            "• N'importe quel défi business\n\n"
            "Tape ta question directement ici 👇",
            parse_mode="Markdown",
            reply_markup=kb_back()
        )
 
    elif d == "rappel_toggle":
        actifs = not context.user_data.get("rappels_actifs", False)
        context.user_data["rappels_actifs"] = actifs
        if actifs:
            msg = ("✅ *Rappels activés !*\n\n"
                   "Tu recevras tes rappels mensuels pour ne jamais oublier "
                   "de remplir ton guide. La régularité, c'est la clé ! 💪")
        else:
            msg = ("🔕 *Rappels désactivés.*\n\n"
                   "Tu peux les réactiver à tout moment depuis ce menu.")
        await q.edit_message_text(msg, parse_mode="Markdown", reply_markup=kb_rappels(actifs))
 
async def msg_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texte = update.message.text or ""
mode_ia = context.user_data.get("mode_ia", False)
    
    if mode_ia and texte.strip():
        # Mode IA actif — on envoie la question à Claude
        await update.message.reply_text("⏳ Je réfléchis à ta question...")
        historique = context.user_data.get("historique_ia", [])
        reponse = appel_ia(texte, historique)
        # Mise à jour de l'historique (max 6 messages)
        historique.append({"role": "user", "content": texte})
        historique.append({"role": "assistant", "content": reponse})
        context.user_data["historique_ia"] = historique[-6:]
        await update.message.reply_text(
            reponse + "\n\n_Pose une autre question ou utilise le menu 👇_",
            parse_mode="Markdown",
            reply_markup=kb_main()
        )
        return
 
    # Mode normal — réponses fixes
texte_lower = texte.lower()
    if any(m in texte_lower for m in ["merci", "super", "bien", "parfait", "ok", "top"]):
        rep = "😊 Avec plaisir ! Tape /menu pour accéder aux outils."
    elif any(m in texte_lower for m in ["prix", "tarif", "combien", "marge"]):
        rep = "Pour les prix et marges, utilise le menu 💰 Prix & Marges !"
    elif any(m in texte_lower for m in ["aide", "help", "comment", "quoi"]):
        rep = "Je suis là ! Utilise les boutons du menu pour choisir un sujet."
    else:
        rep = ("Je suis ton assistant business ! 🤖\n\n"
               "Utilise les boutons ci-dessous ou clique 🤖 *Poser une question au coach* "
               "pour me poser n'importe quelle question.")
    await update.message.reply_text(rep, parse_mode="Markdown", reply_markup=kb_main())
 
# ─────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────
def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("menu", menu_cmd))
    app.add_handler(CallbackQueryHandler(buttons))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, msg_handler))
    logger.info("Coach Business Pro - Bot demarre !")
    app.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)
 
if __name__ == "__main__":
    main()


            
            
            
        
        
