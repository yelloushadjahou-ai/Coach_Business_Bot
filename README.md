# Coach Business Pro — Bot Telegram
## Pack : Mon Carnet de Bord Business

---

## Contenu du bot
- 5 menus principaux avec boutons cliquables
- Comptabilité : bénéfice, charges, seuil de rentabilité, trésorerie, stock
- Prix & Marges : tarif horaire, coût de revient, marge, promo, négociation
- Légal & Fiscal : adapté pour Bénin, Côte d'Ivoire, Sénégal, Burkina Faso, Togo
- Aide Guide : comment utiliser le carnet, FAQ, astuce, motivation
- Rappels mensuels : activables/désactivables par l'utilisateur

---

## DÉPLOIEMENT — Étapes à suivre

### Étape 1 — Créer ton bot sur Telegram
1. Ouvre Telegram et cherche @BotFather
2. Envoie /newbot
3. Donne un nom affiché : ex "Coach Business Pro"
4. Donne un username (doit finir par "bot") : ex "CoachBusinessProBot"
5. Copie le TOKEN reçu — il ressemble à : 5823741096:AAFx9k2mN...

### Étape 2 — Créer un compte Railway
1. Va sur railway.app
2. Connecte-toi avec ton compte Google (gratuit)
3. Clique sur "New Project"

### Étape 3 — Déployer le bot
1. Dans Railway, clique "Deploy from GitHub repo"
   OU clique "Empty project" puis "Add service" > "GitHub repo"
2. Si tu n'as pas GitHub : clique "Empty project" > "Add service" > "Template"
   et cherche "Python"
3. Upload les 3 fichiers : bot.py, requirements.txt, Procfile

### Étape 4 — Ajouter ton token
1. Dans ton projet Railway, va dans l'onglet "Variables"
2. Clique "New Variable"
3. Nom : BOT_TOKEN
4. Valeur : colle ton token ici (celui donné par BotFather)
5. Clique "Add"

### Étape 5 — Lancer le bot
1. Railway va automatiquement installer les dépendances et démarrer le bot
2. Va sur Telegram, cherche ton bot par son username
3. Envoie /start — ton bot doit répondre !

---

## Méthode alternative sans GitHub (plus simple depuis téléphone)

1. Va sur railway.app > New Project > Deploy from GitHub
2. Si pas de GitHub, utilise replit.com à la place :
   - Crée un compte sur replit.com (gratuit)
   - Nouveau Repl > Python
   - Upload bot.py et requirements.txt
   - Dans "Secrets" (cadenas), ajoute BOT_TOKEN = ton_token
   - Clique Run
   - Pour que le bot tourne 24h/24, active "Always On" (plan payant)
   - Alternative gratuite : utilise uptimerobot.com pour pinger le bot

---

## Mise à jour du contenu

Pour modifier les réponses du bot, édite les dictionnaires dans bot.py :
- COMPTA = conseils de comptabilité
- PRIX = conseils sur les prix
- PAYS = informations légales par pays
- GUIDE = aide pour utiliser le guide

Chaque clé correspond à un bouton du menu.

---

## Support
Pour toute question technique, contacte-nous via les boutiques.
