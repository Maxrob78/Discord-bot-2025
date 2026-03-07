# ⚽ Discord-bot-2025 | Football RP Engine

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Discord.py](https://img.shields.io/badge/Discord.py-Latest-green.svg)
![Status](https://img.shields.io/badge/Status-En%20D%C3%A9veloppement-orange.svg)

Solution d'automatisation et de gestion d'API pour serveurs **Discord RolePlay (RP) de football**. Ce bot transforme les interactions textuelles et les captures d'écran en une expérience de simulation sportive immersive et automatisée.

---

## 🌟 Fonctionnalités Clés

### 👁️ Reconnaissance Optique (OCR)
Le bot élimine la saisie manuelle fastidieuse. En analysant les captures d'écran des matchs (FIFA, PES, FM), il extrait automatiquement :
* **Scores finaux** et statistiques de match.
* **Buteurs et passeurs** pour la mise à jour des classements individuels.
* **Statistiques collectives** (possession, tirs cadrés).

### ⚙️ Moteur de Simulation (Algorithme)
Un algorithme avancé gère les résultats des matchs en prenant en compte plusieurs variables :
* **Statistiques d'équipe :** Attaque, Milieu, Défense.
* **Facteurs dynamiques :** Forme du moment, avantage à domicile, et gestion des blessures.
* **Aléatoire contrôlé :** Simulation fidèle à l'imprévisibilité du football réel.

### 🎨 Design & Montage Automatisé
Génération instantanée de visuels pour dynamiser la vie du serveur :
* **Feuilles de match :** Création de compositions graphiques avant le coup d'envoi.
* **Cartes de joueurs :** Génération de cartes de statistiques personnalisées (style FUT).
* **Annonces de résultats :** Tableaux de scores stylisés prêts à être partagés.

---

## 🛠️ Stack Technique

| Technologie | Utilisation |
| :--- | :--- |
| **Python** | Langage de programmation principal. |
| **Discord.py** | Framework pour l'interaction avec l'API Discord. |
| **Tesseract / EasyOCR** | Moteur de traitement d'images pour l'extraction de données. |
| **Pillow (PIL)** | Manipulation d'images et création de templates visuels. |
| **JSON** | Stockage léger des données joueurs, équipes et classements. |
| **Datetime** | Gestion des calendriers, logs et délais de récupération. |
