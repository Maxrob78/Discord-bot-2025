import discord
from discord.ext import commands
import json
import os
import random
import asyncio
from math import ceil
import unicodedata
from difflib import SequenceMatcher
from collections import Counter
import random
import datetime
from datetime import date
from discord.ui import View, Button
from discord import Embed, Interaction
from datetime import datetime
from discord.ui import View, Modal, TextInput, button, Select
from discord import Embed
import requests



intents = discord.Intents.default()
intents.members = True  # Très important !
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

BALANCES_FILE = "balances.json"
PLAYERS_FOR_SALE_FILE = "players_for_sale.json"
JOUEURS_POSSEDES_FILE = "joueurs_possedes.json"


# Charger les joueurs possédés
def load_owned_players():
    if not os.path.exists(JOUEURS_POSSEDES_FILE):
        return {}
    with open(JOUEURS_POSSEDES_FILE, "r") as f:
        return json.load(f)


# Sauvegarder les joueurs possédés
def save_owned_players(data):
    with open(JOUEURS_POSSEDES_FILE, "w") as f:
        json.dump(data, f, indent=4)


owned_players = load_owned_players()


# Charger les soldes
def load_balances():
    if not os.path.exists(BALANCES_FILE):
        return {}
    with open(BALANCES_FILE, "r") as f:
        return json.load(f)


def save_balances(balances):
    with open(BALANCES_FILE, "w") as f:
        json.dump(balances, f, indent=4)


# Charger la liste des joueurs en vente
def load_players_for_sale():
    if not os.path.exists(PLAYERS_FOR_SALE_FILE):
        return []
    with open(PLAYERS_FOR_SALE_FILE, "r") as f:
        return json.load(f)


def save_players_for_sale(players):
    with open(PLAYERS_FOR_SALE_FILE, "w") as f:
        json.dump(players, f, indent=4)


balances = load_balances()
players_for_sale = load_players_for_sale()


def get_balance(user_id):
    balances = load_balances()
    return balances.get(str(user_id), 0)


def change_balance(user_id, amount):
    user_id = str(user_id)
    balances = load_balances()  # Recharge à chaque fois
    balances[user_id] = balances.get(user_id, 0) + amount
    save_balances(balances)


@bot.event
async def on_ready():
    print(f'Connecté en tant que {bot.user}')


# --- Commandes déjà existantes (solde, envoyer, donner) ---


def format_money(amount):
    """Formate un nombre avec des espaces tous les 3 chiffres"""
    try:
        amount = int(amount)  # force en entier
    except (ValueError, TypeError):
        return str(amount)
    
    return f"{amount:,}".replace(",", " ")



@bot.command()
async def solde(ctx):
    balances = load_balances()  # Recharge toujours ici
    bal = balances.get(str(ctx.author.id), 0)
    bal_formatted = format_money(bal)
    await ctx.send(f"{ctx.author.mention}, ton solde est de {bal_formatted} €."
                   )


@bot.command()
async def viewsolde(ctx, membre: discord.Member):
    balances = load_balances()
    bal = balances.get(str(membre.id), 0)  # Solde du membre ciblé
    bal_formatted = format_money(bal)
    await ctx.send(f"{membre.display_name} a un solde de {bal_formatted} €.")


@bot.command()
async def kebab(ctx):
    user_id = str(ctx.author.id)
    balances = load_balances()

    if balances.get(user_id, 0) < 8:
        await ctx.send(
            "❌ Tu n'as pas assez d'argent pour acheter un kebab (8 €).")
        return

    balances[user_id] -= 8
    save_balances(balances)
    formatted_solde = format_money(balances[user_id])
    await ctx.send(
        f"🌯 {ctx.author.display_name} a acheté un kebab pour 8 € ! Il lui reste {formatted_solde} €."
    )


@bot.command(name="envoyerkebab")
async def envoyer_kebab(ctx, membre: discord.Member):
    emetteur_id = str(ctx.author.id)
    receveur_id = str(membre.id)
    balances = load_balances()

    if balances.get(emetteur_id, 0) < 8:
        await ctx.send(
            "❌ Tu n'as pas assez d'argent pour offrir un kebab (8 €).")
        return

    balances[emetteur_id] -= 8
    balances[receveur_id] = balances.get(receveur_id, 0) + 8

    save_balances(balances)
    solde_emetteur = format_money(balances[emetteur_id])

    await ctx.send(
        f"🌯 {ctx.author.display_name} a offert un kebab à {membre.display_name} pour 8 € !\nIl lui reste {solde_emetteur} €."
    )


@bot.command(name="nb_kebab")
async def kebabs(ctx, membre: discord.Member = None):
    if membre is None:
        membre = ctx.author

    user_id = str(membre.id)
    balances = load_balances()
    solde = balances.get(user_id, 0)
    nb_kebabs = solde // 8

    solde_formate = format_money(solde)

    if membre == ctx.author:
        await ctx.send(
            f"Tu as {solde_formate} €, tu peux acheter **{nb_kebabs} kebabs** 🌯."
        )
    else:
        await ctx.send(
            f"{membre.display_name} a {solde_formate} €, il peut acheter **{nb_kebabs} kebabs** 🌯."
        )

with open("inventaires.json", "r", encoding="utf-8") as f:
    content = f.read()
print(content[-200:])  # affiche les 200 derniers caractères du fichier

with open("inventaires.json", "r", encoding="utf-8") as f:
    content = f.read()
print("Longueur du contenu :", len(content))
print("Les 500 premiers caractères :\n", content[:500])
print("Les 500 derniers caractères :\n", content[-500:])


try:
    data = json.loads(content)
    print("JSON is valid and loaded.")
except json.JSONDecodeError as e:
    print(f"Erreur JSON: {e}")
    print("Contenu autour de l'erreur :")
    pos = e.pos
    start = max(pos - 40, 0)
    end = pos + 40
    print(content[start:end])


@bot.command()
@commands.has_permissions(administrator=True)
async def poster(ctx, *, args):
    parts = [x.strip() for x in args.split("|")]

    texte = ""
    image_url = None
    titre = "Nouveau post"

    if len(parts) == 1:
        texte = parts[0]
    elif len(parts) == 2:
        texte, titre = parts
    elif len(parts) == 3:
        texte, image_url, titre = parts
    else:
        error = await ctx.send(
            "❌ Format invalide. Utilise : `!poster texte | titre` ou `!poster texte | image_url | titre`"
        )
        await asyncio.sleep(5)
        await error.delete()
        return

    embed = discord.Embed(title=titre,
                          description=texte,
                          color=discord.Color.blue())
    embed.set_footer(text=f"Posté par {ctx.author.display_name}")

    sent_message = None
    # Si une image est fournie via URL
    if image_url:
        embed.set_image(url=image_url)
        sent_message = await ctx.send(embed=embed)

    # Sinon, s’il y a une pièce jointe image
    elif ctx.message.attachments:
        image = ctx.message.attachments[0]
        if image.content_type and image.content_type.startswith("image/"):
            file = await image.to_file()
            embed.set_image(url=f"attachment://{file.filename}")
            sent_message = await ctx.send(file=file, embed=embed)
        else:
            await ctx.send("❌ Le fichier joint n'est pas une image.")
            return
    else:
        sent_message = await ctx.send(embed=embed)

    # Ajouter les réactions automatiquement
    if sent_message:
        await sent_message.add_reaction("💙")
        await sent_message.add_reaction("🔁")
        await sent_message.add_reaction("📤")

    # Supprimer le message d'origine (celui contenant la commande)
    try:
        await ctx.message.delete()
    except discord.errors.Forbidden:
        pass


@bot.command()
@commands.has_permissions(administrator=True)
async def dire(ctx, *, phrase: str):
    auteur = ctx.author.display_name
    salon = ctx.channel.name
    serveur = ctx.guild.name if ctx.guild else "DM"
    date = ctx.message.created_at.strftime("%Y-%m-%d %H:%M:%S")

    print(f"[{date}] {auteur} ({serveur} #{salon}) a dit : {phrase}")

    try:
        await ctx.send(phrase)
        await ctx.message.delete()
    except discord.errors.Forbidden:
        print(f"[ERREUR] Le bot n'a pas pu supprimer le message de {auteur}.")
    except Exception as e:
        print(f"[ERREUR] {type(e).__name__} : {e}")



def proba():
    # Liste des multiplicateurs avec poids
    probabilites = [
        (2.0, 1),   # x2 → gros gain (1%)
        (1.5, 2),   # x1.5 → gain moyen (2%)
        (1.2, 3),   # x1.2 → petit gain (3%)
        (1.0, 20),  # égalité → récupère la mise (20%)
        (0.8, 34),  # perte 20% (34%)
        (0.5, 20),  # perte 50% (20%)
        (0.0, 20),  # tout perdu (20%)
    ]
    multiplicateurs, poids = zip(*probabilites)
    return random.choices(multiplicateurs, weights=poids, k=1)[0]


@bot.command()
async def parie(ctx, mise: int):
    if mise <= 0:
        return await ctx.send("⚠ La mise doit être un entier positif.")

    user_id = str(ctx.author.id)
    balances = load_balances()
    solde = balances.get(user_id, 0)

    if mise > solde:
        return await ctx.send(
            f"💸 Tu n'as pas assez d'argent pour parier {format_money(mise)} €. Ton solde est de {format_money(solde)} €."
        )

    # Effet suspense
    msg = await ctx.send(f"🎰 {ctx.author.mention} lance la roue de la fortune...")
    await asyncio.sleep(1)
    await msg.edit(content=f"🎰 La roue tourne... 🔄")
    await asyncio.sleep(1)
    await msg.edit(content=f"🎰 Suspense... 🔥")
    await asyncio.sleep(1)

    gain_ratio = proba()
    resultat = int(mise * gain_ratio)
    benefice_net = resultat - mise

    # Mise à jour du solde
    nouveau_solde = max(solde - mise + resultat, 0)
    balances[user_id] = nouveau_solde
    save_balances(balances)

    # Message final
    if benefice_net > 0:
        await msg.edit(content=(
            f"🎉 Jackpot {ctx.author.mention} !\n"
            f"Tu gagnes **{format_money(benefice_net)} €** (+ mise récupérée : {format_money(resultat)} €) 💰\n"
            f"💵 Nouveau solde : {format_money(nouveau_solde)} €"
        ))
    elif benefice_net < 0:
        await msg.edit(content=(
            f"💀 Pas de chance {ctx.author.mention}... Tu perds **{format_money(abs(benefice_net))} €** 😢\n"
            f"💵 Nouveau solde : {format_money(nouveau_solde)} €"
        ))
    else:
        await msg.edit(content=(
            f"😐 Égalité {ctx.author.mention}, tu récupères juste ta mise.\n"
            f"💵 Nouveau solde : {format_money(nouveau_solde)} €"
        ))


@bot.command()
async def envoyer(ctx, member: discord.Member, amount: int):
    if amount <= 0:
        await ctx.send("Le montant doit être positif.")
        return
    sender_id = ctx.author.id
    receiver_id = member.id
    sender_bal = get_balance(sender_id)
    if sender_bal < amount:
        await ctx.send("Tu n'as pas assez d'argent pour envoyer cette somme.")
        return
    if receiver_id == sender_id:
        await ctx.send("Tu ne peux pas t'envoyer de l'argent à toi-même.")
        return

    change_balance(sender_id, -amount)
    change_balance(receiver_id, amount)
    print(f"{ctx.author.mention} a envoyé {amount} € à {member.mention}.")
    await ctx.send(
        f"{ctx.author.mention} a envoyé {format_money(amount)} € à {member.mention}."
    )


@bot.command()
async def donner(ctx, member: discord.Member, amount: int):
    # Autoriser uniquement certains IDs
    allowed_ids = [1397942510407516170, 511579819960565773]
    if ctx.author.id not in allowed_ids:
        await ctx.send("🚫 Vous n'êtes pas autorisé à utiliser cette commande.")
        return

    if amount <= 0:
        await ctx.send("Le montant doit être positif.")
        return

    change_balance(member.id, amount)
    print(f"{ctx.author.mention} a donné {amount} € à {member.mention}.")
    await ctx.send(
        f"{ctx.author.mention} a donné {amount} € à {member.mention}.")


@donner.error
async def donner_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("Tu dois être admin pour utiliser cette commande.")


@envoyer.error
async def envoyer_error(ctx, error):
    if isinstance(error, commands.BadArgument):
        await ctx.send(
            "Merci de mentionner un utilisateur valide et un montant entier.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Usage: !envoyer @utilisateur montant")


# --- Nouvelle commande pour mettre un joueur en vente ---


@bot.command()
@commands.has_any_role("CM", "Admin",
                       "Club")  # Seuls les admins et ceux avec le rôle "club"
async def vendrejoueur(ctx, nom: str, age: int, note: int, valeur: int):
    if age <= 0 or age >= 45 or note < 0 or note > 100 or valeur <= 0:
        await ctx.send(
            "Veuillez entrer des valeurs valides : age > 0 et <46, note entre 0 et 100, valeur > 0."
        )
        return

    joueur = {
        "nom": nom,
        "age": age,
        "note": note,
        "valeur": valeur,
        "vendeur_id": ctx.author.id,
        "vendeur_nom": str(ctx.author)
    }

    players_for_sale.append(joueur)
    save_players_for_sale(players_for_sale)
    await ctx.send(
        f"Le joueur {nom} a été mis en vente pour {valeur} € par {ctx.author.mention}."
    )


# --- Commande pour afficher les joueurs à vendre avec bouton d'achat ---

lock_achat = asyncio.Lock()


class AcheterBouton(discord.ui.Button):
    channel_id = 1401847960601362533  # Remplace avec ton channel ID
    channel = bot.get_channel(channel_id)

    def __init__(self, joueur, bot):
        super().__init__(
            label=f"Acheter {joueur['nom']} ({joueur['valeur']} €)",
            style=discord.ButtonStyle.green)
        self.joueur = joueur
        self.bot = bot

    async def callback(self, interaction: discord.Interaction):
        # Récupérer les rôles de l'utilisateur qui clique
        roles = [role.name for role in interaction.user.roles]

        # Vérifier s'il a le rôle "Admin" ou "club"
        if "Admin" not in roles and "Club" not in roles:
            await interaction.response.send_message(
                "❌ Tu n'as pas la permission d'acheter ce joueur.",
                ephemeral=True)
            return

        # Ton code existant de gestion de l'achat...
        async with lock_achat:
            acheteur_id = str(interaction.user.id)
            vendeur_id = str(self.joueur['vendeur_id'])
            valeur = self.joueur['valeur']

            global players_for_sale
            print(
                f"[DEBUG] Achat demandé par {interaction.user} pour {self.joueur['nom']}"
            )

            en_vente = any(p['nom'] == self.joueur['nom']
                           and str(p['vendeur_id']) == vendeur_id
                           for p in players_for_sale)
            print(f"[DEBUG] Joueur en vente ? {en_vente}")

            message_reponse = None

            if not en_vente:
                message_reponse = "Désolé, ce joueur a déjà été vendu."
                print("[DEBUG] Joueur déjà vendu")

            elif get_balance(acheteur_id) < valeur:
                message_reponse = "Tu n'as pas assez d'argent pour acheter ce joueur."
                print("[DEBUG] Pas assez d'argent")

            elif acheteur_id == vendeur_id:
                message_reponse = "Tu ne peux pas acheter ton propre joueur."
                print("[DEBUG] Achat de son propre joueur interdit")

            elif acheteur_id in owned_players:
                for p in owned_players[acheteur_id]:
                    if p['nom'] == self.joueur['nom'] and p.get(
                            'ancien_vendeur') == self.joueur['vendeur_nom']:
                        message_reponse = "Tu possèdes déjà ce joueur."
                        print("[DEBUG] Joueur déjà possédé")
                        break

            if message_reponse is not None:
                await interaction.response.send_message(message_reponse,
                                                        ephemeral=True)
                return

            # Effectuer l'achat
            change_balance(acheteur_id, -valeur)
            change_balance(vendeur_id, valeur)

            if acheteur_id not in owned_players:
                owned_players[acheteur_id] = []

            owned_players[acheteur_id].append({
                "nom":
                self.joueur["nom"],
                "age":
                self.joueur["age"],
                "note":
                self.joueur["note"],
                "valeur":
                self.joueur["valeur"],
                "ancien_vendeur":
                self.joueur["vendeur_nom"]
            })
            save_owned_players(owned_players)

            players_for_sale = [
                p for p in players_for_sale
                if not (p['nom'] == self.joueur['nom']
                        and str(p['vendeur_id']) == vendeur_id)
            ]
            save_players_for_sale(players_for_sale)
            print(
                f"[DEBUG] Joueur {self.joueur['nom']} retiré de la vente et sauvegardé."
            )

            try:
                vendeur = await self.bot.fetch_user(int(vendeur_id))
                if vendeur:
                    await vendeur.send(
                        f"Ton joueur {self.joueur['nom']} a été vendu à {interaction.user.name} pour {valeur} €."
                    )
                    print(f"[DEBUG] MP envoyé au vendeur {vendeur_id}")
            except Exception as e:
                print(
                    f"Impossible d’envoyer un MP au vendeur {vendeur_id}: {e}")

            await interaction.response.send_message(
                f"{interaction.user.mention} a acheté {self.joueur['nom']} pour {valeur} €.",
                ephemeral=False  # ou True si tu veux que seul l'acheteur le voie
            )
            print("[DEBUG] Message de confirmation envoyé à l'acheteur.")

            await channel.send(
                f"{interaction.user.mention} a acheté {self.joueur['nom']} pour {valeur} €."
            )
            print("Message envoyé.")


# Liste simple de questions (question, réponse)
quiz_questions = [
    # Histoire / Géographie
    ("En quelle année a eu lieu la Révolution française ?", "1789"),
    ("En quelle année a eu lieu l'indépendance du Vietnam ?", "1945"),
    ("Quelle est la capitale du Vietnam ?", "Hanoï"),
    ("Quelle baie naturel est dans les 'sept merveilles de la nature' ?",
     "Baie de Ha Long"),
    ("En quelle année a eu lieu la première guerre mondiale ?", "1914"),
    ("Dans quel continent se situe Tuvalu ?", "océanie"),
    ("Dans quel pays est extrait le plus d'uranium ?", "australie"),
    ("Quelle est la capitale de la France ?", "paris"),
    ("Quelle est la capitale de l’Italie ?", "rome"),
    ("Quelle est la capitale de l’Australie ?", "canberra"),
    ("Quel pays est surnommé le pays du Soleil-Levant ?", "japon"),
    ("Quel est le plus grand désert du monde ?", "antarctique"),
    ("Quel est le plus grand océan du monde ?", ["océan pacifique","pacifique"]),
    ("Quel est le plus haut sommet du monde ?", ["mont everest","everest"]),

    # Sciences / Chimie / Physique
    ("Quel est l'élément chimique dont le symbole est O ?", "oxygène"),
    ("Quel est l'élément chimique dont le symbole est N ?", "azote"),
    ("Quel est l'élément chimique dont le symbole est H ?", "hydrogène"),
    ("Quel est l'élément chimique dont le symbole est C ?", "carbone"),
    ("Quel est l'élément chimique dont le symbole est Fe ?", "fer"),
    ("Quel est l'élément chimique dont le symbole est Au ?", "or"),
    ("Quel est l'élément chimique dont le symbole est Ag ?", "argent"),
    ("Quel est l'élément chimique dont le symbole est Pb ?", "plomb"),
    ("Quel est l'élément chimique dont le symbole est He ?", "hélium"),
    ("Quel est l'élément chimique dont le symbole est Na ?", "sodium"),
    ("Quel est l'élément chimique dont le symbole est K ?", "potassium"),
    ("Quel est l'élément chimique dont le symbole est Ca ?", "calcium"),
    ("Quel est l'élément chimique dont le symbole est Cl ?", "chlore"),
    ("Quel est l'élément chimique dont le symbole est Mg ?", "magnésium"),
    ("Quel est l'élément chimique dont le symbole est Zn ?", "zinc"),
    ("Quel est le gaz le plus présent dans l'air ?", "azote"),
    ("Quelle est la formule chimique de l'eau ?", "h2o"),
    ("Quelle est la formule de l’énergie cinétique ?", "0.5mv²"),
    ("Quelle est la formule du théorème de Pythagore ?", "a² + b² = c²"),
    ("Quelle est la formule de l’énergie (selon Einstein) ?", "e=mc²"),

    # Mathématiques
    ("Combien font 725 / 10 ?", "72,5"),
    ("Combien font 12 × 12 ?", "144"),
    ("Quelle est la dérivée de x² ?", "2x"),
    ("Quelle est la dérivée de cos(x) ?", "-sin(x)"),
    ("Quelle est la primitive de 14 ?", "14x"),
    ("Que vaut log(100) en base 10 ?", "2"),
    ("Quelle est la racine carrée de 169 ?", "13"),

    # Culture générale
    ("Qui a écrit Les Misérables ?", "victor hugo"),
    ("Qui a peint la Joconde ?", "léonard de vinci"),
    ("Qui a écrit Roméo et Juliette ?", "william shakespeare"),
    ("Qui est le réalisateur de Star Wars ?", "george lucas"),
    ("Quel groupe a chanté Bohemian Rhapsody ?", "queen"),
    ("Quel super-héros est aussi appelé l'homme d'acier ?", "superman"),

    # Sport
    ("Combien de joueurs y a-t-il dans une équipe de football sur le terrain ?",
     "11"),
    ("Dans quel sport utilise-t-on un volant ?", ["badminton","course","f1","railly","moto"]),
    ("Combien de joueurs composent une équipe de basketball sur le terrain ?",
     "5"),
    ("Quel joueur a gagné le ballon d'or en 2007 ?", "kaka"),
    ("Quel club est souvent accusé de tricherie ?", ["real madrid","madrid","real"]),
    ("Qui a remporté la Coupe du Monde 2018 ?", "france"),
    ("Qui a marqué le but en finale de la Coupe du Monde 2010 ?",
     ["andres iniesta","iniesta"]),
    ("Quel joueur est surnommé le pharaon ?", ["mohamed salah","salah"]),
    ("Quel club a remporté la Ligue des Champions 2023 ?", ["manchester city","city","man city"]),
    ("Quel joueur détient le record de buts en Ligue des Champions ?",
     ["cristiano ronaldo","cr7","ronaldo"]),
    ("Quel pays a organisé la Coupe du Monde 2014 ?", "brésil"),
    ("Qui a remporté l'Euro 2016 ?", "portugal"),
    ("Combien de Coupes du Monde a gagné le Brésil ?", "5"),
    ("Qui est le meilleur buteur de l'histoire du football ?",
     ["cristiano ronaldo","cr7","ronaldo"]),
    ("Quel joueur est surnommé la pulga ?", ["Lionel Messi","messi",'léo messi',"lionel","lm10"]),
    ("Quel joueur a gagné le plus de Ballons d'or ?", ["Lionel Messi","messi",'léo messi',"lionel","lm10"]),
    ("Quel club est surnommé les reds ?", "liverpool"),
    ("Quel stade est le plus grand du monde en capacité ?",
     "rungrado 1er mai"),
    ("Qui a gagné la Coupe du Monde 2006 ?", "italie"),
    ("Quel joueur a marqué un triplé contre l'Espagne en Coupe du Monde 2018 ?",
     ["cristiano ronaldo","cr7","ronaldo"]),
    ("Quel club a remporté la première Ligue des Champions en 1956 ?",
     ["real madrid","madrid","real"]),
    ("Quel pays a remporté l'Euro 1992 avec une équipe appelée en urgence ?",
     "danemark"),
    ("Quel joueur a raté un penalty en finale de la Coupe du Monde 1994 ?",
     ["roberto baggio","baggio"]),
    ("Quel gardien a gagné le Ballon d'Or en 1963 ?", ["lev yachine","yachine"]),
    ("Quel club a remporté le plus de championnats d'Angleterre ?",
     ["manchester united","man u","man united"]),
    ("Quel joueur a inscrit 13 buts en une seule Coupe du Monde ?",
     "just fontaine"),
    ("Contre quel pays l'Allemagne a-t-elle perdu 7-5 en 1954 avant de le battre en finale ?",
     "hongrie"),
    ("Qui était sélectionneur de la France lors de la Coupe du Monde 2002 ?",
     "roger lemerre"),
    ("Quel joueur a été transféré pour 222 millions d'euros ?", "neymar"),
    ("Quel joueur a été exclu en finale de la Coupe du Monde 2006 ?",
     ["Zinedine Zidane","zidane","zizou","zinedine"]),
    ("Qui a remporté la Ligue des Nations en 2019 ?", "portugal"),
    ("Quel club argentin joue au stade Monumental ?", "river plate"),
    ("Quel club est surnommé 'les colchoneros' ?", "atletico madrid"),
    ("Qui a été le plus jeune joueur à disputer une Coupe du Monde ?",
     "norman whiteside"),
    ("Quel joueur a terminé meilleur buteur de la Coupe du Monde 2014 ?",
     ["james rodriguez","rodriguez"]),
    ("En 1943, que subit le Barça avant un 11-1 contre le Real ?", "menaces"),
    ("Quel score a été enregistré au retour Real-Barça en 1943 ?", "11-1"),
    ("Sous quel régime le Real a été favorisé ?", "franquiste"),
    ("Qui dirigeait l’Espagne quand le Real était aidé ?", "franco"),
    ("Quel club est lié à des aides politiques dans les années 40-50 ?",
     ["real madrid","madrid","real"]),
    ("Quel pays a remporté la Coupe du Monde 2006 ?", "italie"),
    ("Qui a marqué en finale de la Coupe du Monde 2002 ?", ["Ronaldo","r9","ronaldo nazario"]),
    ("Quel club italien a été relégué pour corruption en 2006 ?", "juventus"),
    ("Quel est le club rival du Real Madrid ?", ["barcelone","barca"]),
    ("Quel est le nom du stade du FC Barcelone ?", "camp nou"),
    ("Quel pays a remporté l’Euro 2004 ?", "grèce"),
    ("Quel joueur a gagné le Ballon d'Or en 1995 ?", ["George Weah","weah"]),
    ("Quelle équipe a remporté la Coupe Intertoto en 2001 ?", "aston villa"),
    ("Quel joueur a reçu un carton rouge après 10 secondes de jeu ?",
     ["giuseppe lorenzo","lorenzo"]),
    ("Combien de buts a marqué Just Fontaine en une seule Coupe du Monde ?",
     "13"),
    ("Quelle équipe a été suspendue de la Coupe du Monde 1994 ?", "chili"),
    ("Quelle année a eu lieu le drame du Heysel ?", "1985"),
    ("Quel joueur a été transféré de Dortmund à Manchester City en 2022 ?",
     ["Erling Haaland","haaland"]),
    ("Dans quel club Eden Hazard a-t-il joué avant le Real Madrid ?",
     "chelsea"),
    ("Quel club a gagné la Liga en 2021 ?", ["atletico madrid","altetico"]),
    ("Qui a terminé meilleur buteur de la Coupe du Monde 2014 ?",
     ["james rodriguez","rodriguez"]),
    ("Quel club belge joue ses matchs au stade Jan Breydel ?", ["club brugge","brugge"]),
    ("Quel joueur a raté le tir au but décisif pour l'Angleterre à l’Euro 2021 ?",
     ["Bukayo saka","saka"]),
    ("Quel club est surnommé les Rossoneri ?", ["ac milan","milan"]),
    ("Qui est le meilleur buteur de l’histoire du Real Madrid ?",
     ["cristiano ronaldo","cr7","ronaldo"]),
    ("Quel joueur a inscrit une bicyclette contre la Juventus en 2018 en C1 ?",
     ["cristiano ronaldo","cr7","ronaldo"]),
    ("Quel pays a organisé la Coupe du Monde 2002 avec le Japon ?",
     "corée du sud"),
    ("Quel gardien allemand a gagné le Mondial 2014 ?", ["manuel neuer","neuer"]),
    ("Combien de Ligue des Champions possède le Barça (jusqu’en 2023) ?", "5"),
    ("Quel club turc porte les couleurs jaune et rouge ?", "galatasaray"),
    ("Quel joueur a marqué en demi-finale France-Belgique en 2018 ?",
     ["Samuel umtiti","umtiti"]),
    ("Qui a remporté le Ballon d’Or 2018 ?", "Luka modric"),
    ("Quel joueur argentin a joué pour Naples dans les années 80 ?",
     ["Diego maradona","maradona"]),
    ("Quel club argentin est surnommé les Millionarios ?", "river plate"),
    ("Quel club a remporté la Ligue des Champions en 1999 ?",
     ["manchester united","man u","man united"]),
    ("Quel pays a remporté la CAN 2012 ?", "zambie"),
    ("Qui a marqué contre l’Argentine en 2014 en finale ?", ["mario götze","gotze"]),
    ("Quel club a été accusé de dopage organisé dans les années 90 ?",
     ["marseille","om"]),
    ("Quel joueur français a été impliqué dans une affaire de mœurs en 2010 ?",
     ["Franck ribéry","ribery"]),
    ("Quel club espagnol a reçu une aide publique illégale selon l’UE ?",
     ["real madrid","madrid","real"]),
    ("Quel joueur argentin est célèbre pour sa 'main de Dieu' ?",
     ["Diego maradona","maradona"]),
    ("Quel pays a été exclu du Mondial 1994 pour guerre ?", "yougoslavie"),
    ("Quel club a été accusé de fraude fiscale en 2016 ?", ["barcelone","barca"]),
    ("Quel président de la FIFA a été suspendu en 2015 ?", "blatter"),
    ("Quel club français a perdu un titre sur tapis vert en 1993 ?",
     ["marseille","om"]),
    ("Quel joueur brésilien a été emprisonné pour viol en 2023 ?",
     ["daniel alves","alves"]),
    ("Quel scandale a éclaté en 2015 autour de la FIFA ?", "fifagate"),
    ("Quel ancien dirigeant de l’UEFA a été mis en examen ?",
     ["michel platini","platini"]),
    ("Quel pays a été accusé de corruption pour l’attribution du Mondial 2022 ?",
     "qatar"),
    ("Quel joueur a échappé à la prison en Espagne pour fraude fiscale ?",
     ["Lionel Messi","messi",'léo messi',"lionel","lm10"]),
    ("Quel club turc a été banni des compétitions européennes ?",
     "fenerbahçe"),
    ("Quel match est surnommé 'la honte de Gijón' ?", ["allemagne-autriche","allemagne autriche"]),
    ("Quel club a vu son stade interdit après des insultes racistes en 2023 ?",
     "valence"),
    ("Quel joueur anglais a parié sur ses propres matchs ?", ["joey barton","barton"]),
    ("Quel président de club a été emprisonné pour blanchiment d’argent ?",
     ["bernard tapie","tapie"]),
    ("Quel pays a truqué des documents pour aligner un joueur au Mondial 2022 ?",
     "équateur"),
    ("Quel club belge a été au cœur d’un scandale de matchs truqués en 2018 ?",
     "anderlecht"),
    ("Quel joueur a agressé un supporter avec un coup de pied sauté ?",
     ["éric cantona","cantona"]),
    ("Quel club a licencié un coach pour avoir dénoncé un viol ?", "levante"),
    ("Quel joueur a été accusé d’avoir payé l’arbitre d’un match de C1 ?",
     ["sergio ramos","ramos"]),
    ("Quel match du PSG a été entaché d’accusations de corruption en 2020 ?",
     ["psg basaksehir","psg-basaksehir","basaksehir"]),
    ("Quel pays a été exclu de l’Euro 1992 à cause d’une guerre ?",
     "yougoslavie"),
    ("Quel joueur a été suspendu pour avoir mordu un adversaire ?",
     ["luis suarez","suarez"]),
    ("Quel club français a refusé de jouer à cause de menaces de mort en 2023 ?",
     "ajaccio"),
    ("Quel joueur a remporté le Soulier d'Or européen en 2023 ?",
     ["Erling Haaland","haaland"]),
    ("Quel club espagnol est surnommé 'Les Chauves-Souris' ?", "Valence"),
    ("Quel est le pays d’origine de l’entraîneur José Mourinho ?", "Portugal"),
    ("Quel joueur a joué pour le Barça, le Real Madrid et l’Inter Milan ?",
     ["Luis Figo","figo"]),
    ("Quel club portugais joue au stade de la Luz ?", ["Benfica","sl Benfica"]),
    ("Quel joueur a porté le numéro 7 à Manchester United après Cristiano Ronaldo ?",
     ["Memphis Depay","depay","menphis"]),
    ("Quel club a remporté la Coupe du Roi en Espagne en 2022 ?",
     ["Real Betis","betis"]),
    ("Quel joueur espagnol a marqué lors de deux finales d’Euro ?",
     ["David Silva","silva"]),
    ("Quel pays a battu l'Allemagne en demi-finale de la Coupe du Monde 2006 ?",
     "Italie"),
    ("Quel club allemand est surnommé 'Die Schwarzgelben' ?",
     ["Borussia Dortmund","dortmund"]),
    ("Quel joueur français a été capitaine lors de la finale de la Coupe du Monde 2006 ?",
     ["Zinedine Zidane","zidane","zizou","zinedine"]),
    ("Dans quel club Franck Ribéry a-t-il terminé sa carrière ?",
     "Salernitana"),
    ("Quel est le record de buts dans un seul match de Ligue 1 ?", "12"),
    ("Quel joueur africain a remporté le Ballon d’Or africain 4 fois ?",
     ["Yaya Touré","touré"]),
    ("Quel club espagnol a été promu en Liga en 2023 après 21 ans ?",
     ["Granada","grenade"]),
    ("Quel joueur a marqué un but de la tête en finale de C1 2009 ?",
     ["Lionel Messi","messi",'léo messi',"lionel","lm10"]),
    ("Quel ancien joueur est devenu président du Liberia ?", ["George Weah","weah"]),
    ("Quel club de Ligue 1 a une mascotte nommée 'Minga' ?", ["RC Lens","lens"]),
    ("Quel est le pays d’origine du club Al-Nassr ?", "Arabie saoudite"),
    ("Quel joueur a reçu un carton rouge après 2 fautes en 2 minutes lors de l’Euro 2016 ?",
     ["Granit Xhaka","xhaka"]),
    ("Quel joueur portugais a marqué un doublé contre la France à l’Euro 2020 ?",
     ["cristiano ronaldo","cr7","ronaldo"]),
    ("Quel joueur français a été transféré de Lyon au PSG en 2024 ?",
     ["Bradley Barcola","barcola","bb29","bradley"]),
    ("Quel club a remporté la Ligue Europa en 2023 ?", ["Séville","fc séville"]),
    ("Quel joueur a porté le numéro 10 au PSG avant Neymar ?",
     ["Zlatan Ibrahimovic","zlatan","ibra","ibrahimovic"]),
    ("Quel club anglais est surnommé 'The Toffees' ?", "Everton"),
    ("Quel joueur a été élu meilleur jeune de la Coupe du Monde 2022 ?",
     ["Enzo Fernández","enzo","fernandez"]),
    ("Quel est le club formateur de Riyad Mahrez ?", "Quimper"),
    ("Quel joueur a marqué un triplé en finale de la Coupe du Monde 2022 ?",
     ["kylian mbappé","mbappé","kylian","kiki","kiki de bondy","km7"]),
    ("Qui était capitaine de l’Argentine lors de la Coupe du Monde 1986 ?",
     ["Diego Maradona","maradona"]),
    ("Quel entraîneur a mené l'Italie au titre européen en 2021 ?",
     "Roberto Mancini"),
    ("Quel club écossais dispute l’Old Firm contre le Celtic ?", "Rangers"),
    ("Quel joueur a inscrit le premier but de l’histoire de la Coupe du Monde ?",
     ["Lucien Laurent","lucien","laurent"]),
    ("Quel est le club de formation de Karim Benzema ?", ["Olympique lyonnais","ol","lyon"]),
    ("Quel stade accueille les matchs du Bayern Munich ?", "Allianz Arena"),
    ("Quel club ukrainien a remporté la Coupe UEFA en 2009 ?",
     ["Shakhtar Donetsk","Shakhtar"]),
    ("Quel club saoudien a recruté Karim Benzema en 2023 ?", ["Al-Ittihad","ittiad"]),
    ("Quel pays a remporté la première édition de l’Euro en 1960 ?", ["URSS","russie"]),
    ("Quel gardien espagnol a gagné l’Euro 2008, 2012 et la Coupe du Monde 2010 ?",
     ["Iker Casillas","casillas"]),
    ("Quel joueur brésilien est surnommé 'O Fenômeno' ?", ["Ronaldo","r9","ronaldo nazario"]),
    ("Quel club du rp mobcraft est le plus titré ?", "FC Renard"),
    ("Quel club du rp mobcraft est représenté par un peroquet ?", "FC Parrot"),
    ("Quel club du rp mobcraft était représenté par un diamant et un lyon ?",
     "AS Vorlyons"),
    ("Quel joueur du rp mobcraft à remporté 5 ballons d'or ?", "Fuzety"),
    ("Quel club du rp mobcraft est géré par le joueur mattéo jr et the unique R ?",
     ["FC Calamar","calamar"]),
    ("Quel club du rp mobcraft esr géré par le joueur Diego ?", ["FC Dragão","dragao"]),
    ("Quel club a remporté la ldc en 2025 ?", ["PSG","paris"]),
    ("Quel club a remporté la ldc en 2020 ?", "Bayern munich"),
    ("Quel joueur est le meuilleur buteur du PSG ?", ["kylian mbappé","mbappé","kylian","kiki","kiki de bondy","km7"]),
    ("Quel équipe national est 1er sur l'indice FIFA ?", "Argentine"),
    ("Quel équipe national est 2ème sur l'indice FIFA ?", "Espagne"),
    ("Quel équipe national est 3ème sur l'indice FIFA ?", "France"),

    # Divers
    ("Quelle couleur obtient-on en mélangeant bleu et jaune ?", "vert"),
    ("Combien de pattes a une araignée ?", "8"),
    ("Quel animal est connu pour sa mémoire exceptionnelle ?", "éléphant"),
    ("Quel gaz les plantes absorbent-elles pour faire la photosynthèse ?",
     "co2"),
    ("Combien de couleurs y a-t-il dans un arc-en-ciel ?", "7"),
]

# Variable globale pour stocker les quiz en cours
quiz_en_cours = {}


def normalize(text):
    """Enlève les accents et met en minuscules"""
    text = text.lower()
    return ''.join(
        c for c in unicodedata.normalize('NFD', text)
        if unicodedata.category(c) != 'Mn'
    )

def is_correct(user_input: str, answer):
    """Vérifie si une réponse utilisateur est correcte avec tolérance légère"""
    user_input = normalize(user_input.strip())

    if isinstance(answer, list):
        return any(is_correct(user_input, ans) for ans in answer)

    answer_str = normalize(str(answer).strip())

    # correspondance exacte
    if user_input == answer_str:
        return True

    # tolérance : similarité minimale 80%
    similarity = SequenceMatcher(None, user_input, answer_str).ratio()
    if similarity >= 0.8:
        return True

    return False



@bot.command()
async def quiz(ctx, rounds: int = 3):
    channel_id = ctx.channel.id

    if channel_id in quiz_en_cours:
        await ctx.send("⚠ Un quiz est déjà en cours dans ce salon ! Patiente un peu...")
        return

    quiz_en_cours[channel_id] = True
    await ctx.send(f"🎮 **Début du quiz !** Meilleur sur {rounds} questions gagne le pactole !")

    scores = {}

    for i in range(1, rounds + 1):
        question, answer = random.choice(quiz_questions)
        await ctx.send(f"❓ Question {i}/{rounds} : {question}\nRépondez vite en chat ! (15s)")

        def check(m):
            return m.channel == ctx.channel and not m.author.bot

        end_time = asyncio.get_event_loop().time() + 15
        answered = False

        while True:
            timeout = end_time - asyncio.get_event_loop().time()
            if timeout <= 0:
                break
            try:
                msg = await bot.wait_for('message', timeout=timeout, check=check)
            except asyncio.TimeoutError:
                break

            if is_correct(msg.content, answer):
                user_id = str(msg.author.id)
                gain_base = 100

                # Option : bonus rapidité (facultatif)
                temps_reponse = msg.created_at.timestamp() - ctx.message.created_at.timestamp()
                gain = int(gain_base * 1.5) if temps_reponse < 5 else gain_base

                scores[user_id] = scores.get(user_id, 0) + gain
                balances = load_balances()
                balances[user_id] = balances.get(user_id, 0) + gain
                save_balances(balances)

                await ctx.send(f"🎉 Bravo {msg.author.mention} ! +{gain} € pour cette réponse rapide !")
                answered = True
                break

        if not answered:
            if isinstance(answer, list):
                rep_str = answer[0]   # toujours la première
                await ctx.send(f"⏰ Temps écoulé ! La bonne réponse était : **{rep_str}**")
            else:
                await ctx.send(f"⏰ Temps écoulé ! La bonne réponse était : **{answer}**")


        await asyncio.sleep(2)

    if not scores:
        await ctx.send("Aucun gagnant cette fois, dommage ! 😢")
    else:
        classement = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        leaderboard = []
        for rank, (user_id, score) in enumerate(classement, start=1):
            member = ctx.guild.get_member(int(user_id))
            name = member.display_name if member else f"User {user_id}"
            leaderboard.append(f"**{rank}.** {name} — {score} €")

        await ctx.send("🏆 **Fin du quiz ! Voici le classement final :**\n" + "\n".join(leaderboard))

    del quiz_en_cours[channel_id]





@bot.command()
async def listejoueurs(ctx):
    if not players_for_sale:
        await ctx.send("Aucun joueur n'est en vente pour le moment.")
        return

    # Pour chaque joueur en vente, on affiche un embed avec un bouton d'achat
    for joueur in players_for_sale:
        embed = discord.Embed(
            title=joueur['nom'],
            description=
            f"Âge: {joueur['age']}\nNote: {joueur['note']}\nPrix: {joueur['valeur']} €\nVendu par: {joueur['vendeur_nom']}",
            color=discord.Color.blue())
        view = discord.ui.View()
        view.add_item(AcheterBouton(joueur, bot=bot))
        await ctx.send(embed=embed, view=view)


@bot.command()
async def inventaire(ctx):
    user_id = str(ctx.author.id)
    if user_id not in owned_players or not owned_players[user_id]:
        await ctx.send(f"{ctx.author.mention}, tu ne possèdes aucun joueur.")
        return

    joueurs = owned_players[user_id]
    embed = discord.Embed(
        title=f"🎮 Inventaire de {ctx.author.display_name}",
        description=f"Tu possèdes {len(joueurs)} joueur(s) :",
        color=discord.Color.gold()
    )

    for i, joueur in enumerate(joueurs, start=1):
        embed.add_field(
            name=f"{i}. {joueur['nom']}",
            value=(
                f"Âge: {joueur['age']}\n"
                f"Note: {joueur['note']}\n"
                f"Valeur d'achat: {format_money(joueur['valeur'])} €\n"
                f"Vendu par: {joueur['ancien_vendeur']}"
            ),
            inline=False
        )

    await ctx.send(embed=embed)


INVENTORY_FILE = "inventaires.json"

print("Chemin absolu du fichier :", os.path.abspath(INVENTORY_FILE))


def load_inventory():
    if not os.path.exists(INVENTORY_FILE):
        return {}
    with open(INVENTORY_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_inventory(data):
    with open(INVENTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def test_multiple_json_in_file(filename):
    with open(filename, "r", encoding="utf-8") as f:
        content = f.read()

    decoder = json.JSONDecoder()
    idx = 0
    while idx < len(content):
        content = content.lstrip()
        try:
            obj, idx_new = decoder.raw_decode(content[idx:])
            print(f"JSON object decoded from {idx} to {idx+idx_new}")
            idx += idx_new
            # S’il reste du contenu non vide après l’objet, ça peut poser problème
            rest = content[idx:].strip()
            if rest:
                print(f"Rest content after JSON object: {rest[:30]}...")
            else:
                print("No extra data after JSON object.")
            break
        except json.JSONDecodeError as e:
            print(f"Erreur JSONDecodeError: {e}")
            break

test_multiple_json_in_file("inventaires.json")


def get_bonus(user_id, inventory):
    objets = inventory.get(str(user_id),
                           [])  # on récupère directement la liste
    bonus = 1.0

    if "costume de trader légendaire" in objets:
        bonus += 0.50  # +40% de bonus
    if "lunettes d'expert légendaire" in objets:
        bonus += 0.30
    if "chaussure de salopard légendaire" in objets:
        bonus += 0.30  # +1% de bonus
    if "pentalon Mobcraft légendaire" in objets:
        bonus += 0.30  # +1% de bonus
    if "costume de trader mythique" in objets:
        bonus += 0.30  # +10% de bonus
    if "lunettes d'expert mythique" in objets:
        bonus += 0.20
    if "chaussure de salopard mythique" in objets:
        bonus += 0.20
    if "pentalon Mobcraft mythique" in objets:
        bonus += 0.20
    if "costume de trader rare" in objets:
        bonus += 0.20  # +5% de bonus
    if "lunettes d'expert rare" in objets:
        bonus += 0.10
    if "chaussure de salopard rare" in objets:
        bonus += 0.10
    if "pentalon Mobcraft rare" in objets:
        bonus += 0.10
    if "costume de trader commun" in objets:
        bonus += 0.10  # +2% de bonus
    if "lunettes d'expert commun" in objets:
        bonus += 0.05
    if "chaussure de salopard commun" in objets:
        bonus += 0.05
    if "pentalon Mobcraft commun" in objets:
        bonus += 0.05

    if bonus >= 0.75:
        bonus = 0.75
        # Limite le bonus à 75%

    return bonus
    # Retourne le bonus total


# Liste des objets du shop : nom -> prix

shop_itemsgeek = {
    "PS5 édition limitée": 1200,
    "PS5": 600,
    "PC gamer RGB": 3200,
    "Casque VR 5.0": 2000,
    "Clavier mécanique custom": 700,
    "Carte graphique RTX 5090": 2300,
    "Figurine collector": 250,
    "Affiche rétro Mario": 200,
    "Affiche rétro Zelda": 200,
    "Affiche Mobcraft RP": 150,
    "Tapis de souris XXL": 30,
    "Chaise gaming ergonomique": 800,
    "Manette Xbox Élite": 300,
    "Volant de simulation + pédalier": 1200,
    "Ecran 4K 144Hz": 1800,
    "Setup streaming complet": 4500,
    "Boîtier PC custom RGB": 900,
    "Microphone pro USB": 400,
    "Webcam 4K HDR": 350,
    "Lego Millennium Falcon": 1500,
    "Nintendo Switch OLED": 350,
    "Game Boy édition rétro": 250,
    "Casque audio Hi-Fi": 600,
    "Lampe LED gaming": 100,

    # Ajout téléphones & accessoires
    "iPhone 16 Pro Max": 1300,
    "Samsung Galaxy S25 Ultra": 1200,
    "Google Pixel 9 Pro": 900,
    "iPad Pro": 3800,
    "Samsung Galaxy Tab S10 Ultra": 1500,
    "Apple Watch Series 9": 500,
    "AirPods Pro 2": 300,
    "Batterie externe 20000mAh": 80,
    "Chargeur sans fil rapide": 60,
    "Écouteurs Bose QuietComfort": 280,
    "Support smartphone RGB": 70,
    "Smartphone gaming ASUS ROG Phone 7": 1500,
}

shop_itemsvet = {
    "Costume de trader légendaire": 400000000,
    "lunettes d'expert légendaire": 200000000,
    "chaussure de salopard légendaire": 200000000,
    "Pentalon Mobcraft légendaire": 200000000,
    "Costume de trader mythique": 40000000,
    "lunettes d'expert mythique": 20000000,
    "chaussure de salopard mythique": 20000000,
    "Pentalon Mobcraft mythique": 20000000,
    "Costume de trader rare": 400000,
    "lunettes d'expert rare": 200000,
    "chaussure de salopard rare": 200000,
    "Pentalon Mobcraft rare": 200000,
    "Costume de trader commun": 40000,
    "lunettes d'expert commun": 20000,
    "chaussure de salopard commun": 20000,
    "Pentalon Mobcraft commun": 20000,
    "maillot du Tigre FC": 100,
    "maillot du FC Renard": 100,
    "maillot du FC Parrot": 100,
    "maillot du FC Calamar": 100,
    "maillot du FC Dragão": 100,
    "maillot du FC Noyé": 100,
    "maillot du Sporting Axolotl": 100,
    "maillot du FC Azur": 100,
    "maillot du FC Goat": 100,
    "maillot du Ghast city FC": 100,
    "maillot du Pig FC": 100,
    "maillot de l'Olympique Mouton": 100,
    "maillot du FC Dauphin": 100,
}

shop_itemscar = {
    "Porsche 911 GT2 RS": 289175,
    "Porsche 911 GT3 RS": 248000,
    "Ferrari LaFerrari": 4000000,
    "Aston Martin DBS": 274995,
    "BMW M4 G82": 194100,
    "Bugatti Bolide": 4150000,
    "Ferrari 812 Superfast": 569974,
    "Bugatti Divo": 5000000,
    "Revuelto Spécial": 510000,
    "Lamborghini revuelto": 500000,
    "tofaş yelkenci": 5000,
    "Tuatara Striker": 2200000,
    "Mercedes AMG GT": 134950,
    "Chevrolet Corvette": 132000,
    "Chevrolet Corvette c8 stingray": 250000,
    "Ferrari 458 Italia": 510000,
    "Audi RS6 GT": 192500,
    "Lamborghini Veneno": 10000000,
    "Peugeot 206": 3349,
    "BMW E-tron GT": 128250,
    "Bugatti Chiron": 3200000,
    "Ariel Atom": 79000,
    "Ford Mustang": 59300,
    "koenigsegg regera": 3430000,
    "Koenigsegg Agera": 3100000,
    "Audi RSQ8": 191550,
    "Bentley Continental GT": 293748,
    "Audi RS3": 75000,
    "Opel Astra": 29000,
    "Reliant Supervan III": 20000,
    "Pagani Zonda R": 1746000,
    "Audi M4": 123000,
    "Alpine A110": 65000,
    "Lamborghini Urus": 215000,
    "Ford GT": 400000,
    "Ferrari F12 Berlineta ": 271786,
    "Ferrari 458 Spécial": 415000,
    "Ferrari FXX K": 2400000,
    "Mercedes-Benz E 220": 94000,
    "Ferrari 488 GB": 235000,
    "Rolls-Royce Droptail": 23000000,
    "BMW IX M60": 100000,
    "BMW série 5 G30 ": 58000,
    "Audi A4": 58000,
    "Lexus ES": 60200,
    "BMW I8 Tunning": 165000,
    "Lamborghini Avantador": 380000,
    "Aston Martin Valkyrie": 2500000,
    "Aston Martin Valhalla": 860000,
    "Aston Martin Vanquish": 400000,
    "Aston Martin Vantage": 260000,
    "Mclaren 750s": 280000,
    "Mclaren P1": 1500000,
    "Mclaren Senna": 930000,
    "Mclaren 720s": 250000,
    "Ferrari 488 Chalenge Evo": 260000,
    "Audi RS7 Sportback": 157000,
    "Mercedes-AMG ONE": 2275000,
    "SP Automotive Chaos": 5500000,
    "Aspark Owl": 2500000,
    "Czinger 21C": 2600000,
    "Muray T.50": 2000000,
    "Brabus Rocket 1000": 560000,
    "Porsche 918 Spyder": 775000,
    "KMT Xbow GT-XR": 280000,
    "Lamborghini sian FKP57": 3700000,
    "Maserati MC20": 280000,
    "Lamborghini Huracan": 250000,
    "Ferrari F80": 3600000,
    "Zenvo TSR-S": 1450000,
    "koenigsegg Jesko": 2500000,
    "Hennessey Venom F5": 2400000,
    "Ferrari SF90": 440000,
    "Porsche Taycan": 106000,
    "Porsche Panamera": 119000,
    "BMW M5": 160000,
    "Lamborghini Centanario": 2100000,
    "Ferrari F12TDF": 500000,
    "Mercedes AVTR": 1250000,
    "BMW i4": 70000,
    "Bugatti Tourbillon": 3800000,
    "Bugatti Mistral": 5000000,
    "Daytona SP3": 1968000,
    "GTR R35": 70000,
    "Bugatti Centodieci": 8000000,
    "Bugatti La Voiture Noire": 15900000,
    "Audi R8": 260000,
    "Audi R8 GT2": 300000,
    "Formule 1 Mercedes": 1000000,
    "Rimac Nevera": 2000000,
    "McLaren Speedtail": 2100000,
    "Ferrari Roma": 250000,
    "Audi ABT R8 XGT": 600000,
    "Ferrari 488 Pista": 410000,
    "Apollo INTENSA EMOZIONE": 1050000,
    "Aston Martin Vulcan": 1500000,
    "Chevrolet Camaro GT": 50000,
    "Lamborggini Gallardo": 210000,
    "Lamborghini Sesto": 2700000,
    "Lamborghini Murcielago": 180000,
    "Mercedes-Benz SLR McLaren": 300000
}

shop_itemsvilla = {
    "Villa Les Cèdres (Côte d’Azur)": 380000000,  # Plus chère d'Europe
    "Antilia (Mumbai, 27 étages)": 2100000000,  # Maison la plus chère du monde
    "Villa Leopolda (France)": 500000000,
    "The One (Bel Air, LA)": 295000000,
    "Manoir sur Central Park (NYC)": 75000000,
    "Penthouse One Hyde Park (Londres)": 225000000,
    "Villa en Provence avec piscine": 1600000,
    "Manoir hanté (à rénover)": 350000,
    "maison à Dubaï": 2100000,
    "Maison en bois en Norvège": 480000,
    "Villa au bord du lac (Suisse)": 1300000,
    "Château médiéval (France)": 3800000,
    "Palais Buckingham (Londres)": 5000000000,
    "Palais de Versailles (France, valeur estimée)": 2000000000,
    "Villa Aurora (Rome)": 480000000,
    "Fairfield Pond (NY, USA)": 248000000,
    "Maison à Beverly Hills avec piste d'atterrissage": 320000000,
    "Villa à Miami avec yacht privé inclus": 180000000,
    "Penthouse à Monaco avec toboggan piscine": 310000000,
    "Maison flottante à Dubaï": 12000000,
    "Villa éco-responsable à Bali": 2900000,
    "Loft industriel à Brooklyn": 3200000,
    "Maison de montagne à Aspen": 6700000,
    "Villa japonaise traditionnelle (Kyoto)": 2100000,
    "Villa Art Déco à Los Angeles": 8500000,
    "Villa high-tech à Séoul": 3800000,
    "Riad de luxe à Marrakech": 2100000,
    "Cabane design au Canada": 630000,
    "Villa futuriste en Californie": 12000000,
    "Appartement haussmannien à Paris": 4100000,
    "Maison troglodyte modernisée (Turquie)": 1400000,
    "Chalet en bois aux Alpes": 1900000,
    "Villa sur l’île de Santorin": 2700000,
    "Villa suspendue sur falaises (Mexique)": 3300000,
    "Maison à toit végétal en Suède": 920000,
    "Maison en verre en Finlande": 770000,
    "Maison container ultra moderne": 510000,
    "Maison de campagne avec jardin": 320000,
    "Maison mitoyenne en banlieue": 270000,
    "Pavillon familial 4 chambres": 360000,
    "Villa moderne plain-pied": 450000,
    "Maison traditionnelle avec cheminée": 390000,
    "Villa avec piscine et garage": 620000,
    "Petite maison de ville rénovée": 310000,
    "Maison en lotissement calme": 340000,
    "Villa néo-provençale": 540000,
    "Maison bord de mer (Bretagne)": 570000,
    "Maison avec combles aménagés": 410000,
    "Villa 3 chambres avec terrasse": 490000,
    "Maison ancienne rénovée (centre-ville)": 430000,
    "Maison avec grand terrain": 600000,
    "Maison de plain-pied avec véranda": 380000,
    "Maison à étage avec balcon": 420000,
    "Maison jumelée avec petit jardin": 295000,
    "Maison bois scandinave": 460000,
    "Maison ossature bois écolo": 510000,
    "Maison de lotissement récent": 370000,
    "Maison 2 chambres cosy": 250000,
    "Maison de ville avec garage": 330000,
    "Maison style méditerranéen": 520000,
    "Maison avec vue sur montagne": 590000,
    "Maison avec atelier indépendant": 480000
}

shop_itemsboat = {
    "History Supreme (yacht en or)": 4100000000,  # Le plus cher jamais conçu
    "Eclipse (Roman Abramovich)": 1300000000,
    "Azzam (180m, yacht royal)": 600000000,
    "Flying Fox (136m)": 400000000,
    "Sous-marin personnel de luxe": 35000000,
    "Catamaran Sunreef 80 Power": 8000000,
    "Yacht 30m (avec jacuzzi)": 4200000,
    "Voilier de luxe": 850000,
    "Jet ski Yamaha": 14000,
    "Bateau de pêche customisé": 75000,
    "Catamaran 12m": 690000,
    "Sous-marin personnel": 3200000,
    "Yatch Lamborghini 63": 4000000,
}

shop_itemsplane = {
    "Airbus A380 VIP (Prince saoudien)": 500000000,
    "Boeing 747-8 VIP (Air Force One)": 430000000,
    "Gulfstream G700": 75000000,
    "Dassault Falcon 10X": 75000000,
    "Jet privé Bombardier Global 8000": 78000000,
    "Hydravion militaire reconditionné": 1200000,
    "Jet privé Gulfstream G650": 65000000,
    "Avion de chasse désarmé (collection)": 1900000,
    "Drone militaire reconditionné": 120000,
    "Montgolfière personnalisée": 85000,
    "Hydravion vintage": 350000,
    "Planeur silencieux": 18000,
    # Le plus cher, version royale/prince saoudien
    "Airbus A350-1000": 366000000,
    "Airbus A340-600": 300000000,
    "Airbus A330neo": 270000000,
    "Boeing 747-8 VIP": 430000000,  # Air Force One
    "Boeing 777X VIP": 400000000,
    "Boeing 787 Dreamliner VIP": 325000000,
    "Boeing 737 BBJ MAX": 110000000,
    "Gulfstream G700": 75000000,
    "Dassault Falcon 10X": 75000000,
    "Bombardier Global 8000": 78000000,
    "Cessna Citation Longitude": 27000000,
    "Pilatus PC-24": 11000000,
    "Hydravion militaire reconditionné": 1200000,
}

shop_itemsmoto = {
    "Dodge Tomahawk": 550000,
    "Neiman Marcus Limited Edition Fighter": 110000,
    "Ecosse Spirit ES1": 360000,
    "Harley-Davidson CVO Limited": 50000,
    "Yamaha R1M": 26000,
    "Ducati Panigale V4 R": 45000,
    "Kawasaki Ninja H2R": 55000,
    "BMW HP4 Race": 78000,
    "MV Agusta F4 Claudio": 70000,
    "Confederate FA-13 Combat Bomber": 155000,
    "Lightning LS-218 (électrique)": 38000,
    "Honda RC213V-S": 184000,
    "Aprilia RSV4 1100 Factory": 26000,
    "Suzuki Hayabusa": 18000,
    "Triumph Rocket 3": 24000,
    "Indian Chief Vintage": 28000,
    "Zero SR/F (électrique)": 20000,
    "KTM 1290 Super Duke R": 18000,
    "Bimota Tesi H2": 130000,
    "MV Agusta Brutale 1000 Serie Oro": 90000,
    "Ducati Panigale V4 SP": 40000,
    "BMW S1000RR": 21000,
    "Yamaha YZF-R1": 21000,
    "Harley-Davidson Fat Boy": 21000,
    "KTM 1290 Super Adventure": 20000,
    "Suzuki GSX-R1000": 17000,
    "Honda CBR1000RR-R Fireblade": 28000,
    "Kawasaki Z H2": 16000,
    "Aprilia Tuono V4 1100": 18000,
    "Triumph Street Triple RS": 13000,
    "Indian Scout Bobber": 14000,
    "Zero SR/S (électrique)": 22000,
    "Moto Guzzi V85 TT": 15000,
    "Royal Enfield Himalayan": 5000,
    "Norton Commando 961": 19000,
    "Bajaj Dominar 400": 4000,
}

shop_itemsjewel = {
    "Diamant Pink Star (59,6 carats)": 71000000,
    "Collier L’Incomparable (407 carats)": 55000000,
    "Bague Blue Moon (12 carats)": 48000000,
    "Bague Oppenheimer Blue": 57500000,
    "Collier Heritage in Bloom (Graff Diamonds)": 200000000,
    "Boucles d’oreilles Apollo et Artemis": 57000000,
    "Parure Van Cleef & Arpels": 900000,
    "Collier Fabergé Imperial": 800000,
    "Bracelet Cartier Panthère": 750000,
    "Bague Bulgari Serpenti": 220000,
    "Collier Tiffany & Co. Schlumberger": 1200000,
    "Boucles d’oreilles Cartier classiques": 450000,
    "Collier en diamants noirs": 1800000,
    "Broche Cartier ancienne": 900000,
    "Collier en émeraudes et diamants": 2200000,
    "Bague en rubis Birmanie": 1100000,
    "Bracelet en platine avec saphirs": 1350000,
    "Pendentif en diamant taille cœur": 320000,
    "Boucles d’oreilles en perles naturelles": 280000,
    "Collier en or rose avec opale": 620000,
    "Bague art déco en diamants": 460000,
    "Collier sautoir vintage": 380000,
    "Bracelet manchette en or massif": 710000,
    "Broche florale en diamants": 540000,
    "Pendentif ancien en rubis et or": 370000,
}

shop_itemswatch = {
    "Patek Philippe Grandmaster Chime 6300A": 31000000,
    "Montre Rolex Daytona Paul Newman": 17800000,
    "Montre Graff Diamonds Hallucination": 55000000,
    "Montre Chopard 201-Carat": 25000000,
    "Montre Jaeger-LeCoultre Reverso": 1500000,
    "Vacheron Constantin Tourbillon": 7500000,
    "Richard Mille RM 56-02": 21000000,
    "Montre Audemars Piguet Royal Oak": 3500000,
    "Montre Hublot Big Bang": 5000000,
    "Audemars Piguet Royal Oak Jumbo Extra-Thin": 1200000,
    "Vacheron Constantin Reference 57260": 8000000,
    "Jaeger-LeCoultre Reverso Grande Complication à Triptyque": 1300000,
    "Breguet Grande Complication Marie-Antoinette": 30000000,
    "Omega Speedmaster Professional Moonwatch": 7000,
    "Tag Heuer Monaco": 7000,
    "Breitling Navitimer": 10000,
    "Cartier Santos": 7000,
    "IWC Portugieser Perpetual Calendar": 40000,
    "Panerai Luminor": 10000,
    "Blancpain Fifty Fathoms": 15000,
    "Rolex Submariner": 13000,
    "Seiko Grand Seiko Spring Drive": 9000,
    "A. Lange & Söhne Lange 1": 70000,

    # Ajouts entre 10k et 1M
    "Patek Philippe Nautilus 5711": 350000,  # très rare
    "Rolex GMT-Master II 'Pepsi'": 18000,
    "Rolex Day-Date President": 40000,
    "Audemars Piguet Royal Oak Offshore": 500000,
    "Richard Mille RM 11-03": 2000000,
    "Hublot Big Bang Unico": 220000,
    "Omega Seamaster Diver 300M": 6000,
    "Cartier Ballon Bleu": 12000,
    "TAG Heuer Carrera": 7000,
    "Panerai Radiomir": 13000,
    "Breitling Superocean": 11000,
    "Grand Seiko Snowflake": 15000,
    "IWC Big Pilot": 18000,
    "Jaeger-LeCoultre Master Ultra Thin": 22000,
    "Bulgari Octo Finissimo": 40000,
    "Chopard Mille Miglia": 12000,
    "Tudor Black Bay": 4500,
    "Montblanc TimeWalker": 7000,
    "Zenith Defy Classic": 9000,
    "Nomos Glashütte Tangente": 6000,
    "Panerai Luminor Marina": 13000,
}

shop_itemsart = {
    "Salvator Mundi (Leonardo da Vinci)": 450000000,
    "Les Femmes d’Alger (Picasso)": 179000000,
    "Interchange (Willem de Kooning)": 300000000,
    "The Card Players (Cézanne)": 250000000,
    "Rabbit (Jeff Koons)": 91000000,
    "Nu couché (Modigliani)": 170000000,
    "No. 6 (Violet, Green and Red) (Rothko)": 186000000,
    "Bal du moulin de la Galette (Renoir)": 143000000,
    "The Scream (Munch)": 119900000,
    "Three Studies of Lucian Freud (Bacon)": 142400000,
    "Les Nymphéas (Monet)": 84000000,
    "Portrait of Adele Bloch-Bauer I (Klimt)": 135000000,
    "Garçon à la pipe (Picasso)": 104000000,
    "Portrait of Dr. Gachet (Van Gogh)": 82000000,
    "Woman III (Willem de Kooning)": 137500000,
    "L’Homme au doigt (Modigliani)": 150000000,
    "Flag (Jasper Johns)": 110000000,
    "Black Fire I (Barnett Newman)": 84000000,
    "Number 17A (Jackson Pollock)": 200000000,
    "Les Demoiselles d'Avignon (Picasso)": 180000000,

    # Ajouts 10M - 10k
    "Balloon Dog (Jeff Koons)": 58000000,
    "Portrait of Dora Maar (Picasso)": 45000000,
    "Self-Portrait with Cropped Hair (Frida Kahlo)": 15000000,
    "Campbell's Soup Cans (Andy Warhol)": 11000000,
    "The Persistence of Memory (Dali)": 55000000,
    "Girl with a Pearl Earring (Vermeer)": 30000000,
    "The Night Watch (Rembrandt)": 30000000,
    "Water Lilies (Monet)": 43000000,
    "American Gothic (Wood)": 6500000,
    "Christina's World (Andrew Wyeth)": 7000000,
    "The Kiss (Gustav Klimt)": 24000000,
    "The Birth of Venus (Botticelli)": 20000000,
    "Composition VII (Kandinsky)": 15000000,
    "No. 5, 1948 (Pollock)": 140000000,
    "Campbell's Soup Can (Warhol)": 11000000,
    "Sunflowers (Van Gogh)": 39000000,
    "The Son of Man (Magritte)": 25000000,
    "Portrait of Madame X (Sargent)": 20000000,
    "The Sleeping Gypsy (Rousseau)": 12000000,
    "The Great Wave off Kanagawa (Hokusai)": 9000000,
    "Les Demoiselles d’Avignon (Picasso) - Lithographie": 10000000,
    "Guernica (Picasso) - Reproduction": 10000000,
    "The Blue Boy (Thomas Gainsborough)": 8000000,
    "Nighthawks (Edward Hopper)": 10000000,
    "Whistler's Mother (Whistler)": 9000000,
    "The Girl with the Red Hat (Vermeer)": 6000000,
    "The Arnolfini Portrait (Jan van Eyck)": 7500000,
    "The Dance (Matisse)": 14000000,
    "Broadway Boogie Woogie (Mondrian)": 25000000,
    "The Scream (Munch) - Lithographie": 10000000,
}



per_page = 10
pages = []
current_page = {}


LOOTBOX_TIMES_FILE = "lootbox_times.json"


# Dates d'ouverture de lootbox
def load_lootbox_times():
    if not os.path.exists(LOOTBOX_TIMES_FILE):
        return {}
    with open(LOOTBOX_TIMES_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_lootbox_times(data):
    with open(LOOTBOX_TIMES_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


def is_lootbox_available(user_id, lootbox_times):
    today = date.today().isoformat()
    return lootbox_times.get(user_id) != today


def mark_lootbox_used(user_id, lootbox_times):
    today = date.today().isoformat()
    lootbox_times[user_id] = today


common_items = {
    "Burger": 5,
    "Bouteille d'eau": 3,
    "Casquette": 10,
    "Canette de soda": 2,
    "Barre chocolatée": 1,
    "Glace à l'italienne": 3,
    "Café": 2,
    "Brosse à dents": 4,
    "Stylo": 2,
    "Paire de chaussettes": 6,
    "T-shirt": 15,
    "Pantalon": 20,
}

uncommon_items = {
    "Lampe": 20,
    "Chaise": 15,
    "Écharpe stylée": 18,
    "Enceinte Bluetooth basique": 25,
    "Chargeur rapide": 15,
    "Planche à roulettes": 30,
    "Polo H&M": 20,
    "Mini sac à dos": 25,
    "Tapis de souris RGB": 18,
    "Trépied pour smartphone": 15,
    "Coussin de massage": 20,
    "Casque audio": 25,
}

rare_items = {
    "iPhone 15 Pro Max": 1500,
    "Xiaomi 15 Ultra": 1500,
    "Samsung S25 Ultra": 1500,
    "Sac de sport Nike": 65,
    "Nintendo DS": 90,
    "Xbox One": 250,
    "Xbox Series X": 600,
    "PS4": 250,
    "PS5": 600,
    "PC Gamer RGB": 2100,
    "Nintendo Switch": 300,
    "Nintendo Switch 2": 600,
    "Trotinette électrique": 400,
    "Hoverboard": 280,
    "AirPods Pro": 200,
    "Casque Bose QC": 270,
    "Paire de Jordan 1": 180,
    "TV 4K 55 pouces": 3000,
    "Tablette iPad Pro": 1000,
}

epic_items = {
    "Porsche 911 GT2 RS": 289175,
    "Porsche 911 GT3 RS": 248000,
    "Ferrari LaFerrari": 4000000,
    "Aston Martin DBS": 274995,
    "BMW M4 G82": 194100,
    "Bugatti Bolide": 4150000,
    "Ferrari 812 Superfast": 569974,
    "Bugatti Divo": 5000000,
    "Revuelto Spécial": 510000,
    "Lamborghini Revuelto": 500000,
    "Tofaş Yelkenci": 5000,
    "Tuatara Striker": 2200000,
    "McLaren 765LT": 350000,
    "Audi R8 V10 Plus": 200000,
    "Mercedes AMG GT Black Series": 325000,
    "Chevrolet Corvette Z06": 85000,
    "Tesla Model S Plaid": 135000,
    "Ford Mustang Shelby GT500": 74000,
    "Nissan GT-R Nismo": 210000,
    "Jaguar F-Type SVR": 130000,
    "Alpine A110": 58000,
}

legendary_items = {
    "Île privée": 64000000,
    "Villa à Dubaï": 38000000,
    "Maison à Los Angeles": 40000000,
    "Jet privé": 50000000,
    "Yacht de luxe": 60000000,
    "Villa à New York": 80000000,
    "Villa en Californie": 70000000,
    "Manoir en France": 25000000,
    "Château en France": 20000000,
    "Manoir en Angleterre": 30000000,
    "Sous-marin personnel": 3000000,
    "Maison dans l’espace": 270000000,
    "Yacht privé": 200000000,
    "Le Codex Leicester de Léonard de Vinci": 30800000,
    "Penthouse à Monaco": 330000000,
    "Manoir en Écosse": 25000000,
    "Manoir en Irlande": 25000000,
    "Château en Écosse": 45000000,
    "Île des Maldives privée": 120000000,
    "Palais à Versailles": 200000000,
    "Collection de diamants rares": 95000000,
    "Avion de chasse privé": 90000000,
    "Œuvre originale Picasso": 150000000,
}

# Couleurs par rareté
RARITY_STYLES = {
    "Commun": {"color": discord.Color.greyple(), "emoji": "🥤"},
    "Inhabituel": {"color": discord.Color.green(), "emoji": "📱"},
    "Rare": {"color": discord.Color.blue(), "emoji": "🎮"},
    "Épique": {"color": discord.Color.purple(), "emoji": "🏎️"},
    "Légendaire": {"color": discord.Color.gold(), "emoji": "👑"},
}

# Tables de loot avec labels de rareté
loot_tables = [
    ("Commun", common_items, 0.30),
    ("Inhabituel", uncommon_items, 0.30),
    ("Rare", rare_items, 0.27),
    ("Épique", epic_items, 0.12),
    ("Légendaire", legendary_items, 0.01),
]


@bot.command()
async def lootbox(ctx):
    user_id = str(ctx.author.id)
    inventory = load_inventory()
    lootbox_times = load_lootbox_times()

    if not is_lootbox_available(user_id, lootbox_times):
        await ctx.send("❌ Tu as déjà ouvert ta lootbox aujourd’hui. Reviens demain !")
        return

    # Sélection de la rareté
    rarities, dicts, weights = zip(*loot_tables)
    idx = random.choices(range(len(rarities)), weights=weights, k=1)[0]
    rarity, selected_dict = rarities[idx], dicts[idx]

    # Choix d’un item
    item = random.choice(list(selected_dict.keys()))
    valeur = selected_dict[item]
    valeur_fmt = format_money(valeur)

    # Ajout à l’inventaire
    inventory.setdefault(user_id, []).append(item)
    save_inventory(inventory)

    # Marque lootbox comme utilisée
    mark_lootbox_used(user_id, lootbox_times)
    save_lootbox_times(lootbox_times)

    # Embed initial
    msg = await ctx.send("📦 Tu ouvres ta lootbox...")

    # Animations différentes selon la rareté
    animation_sequences = {
        "Commun": ["📦 Ouvre lentement...", "✨ Une lueur pâle..."],
        "Inhabituel": ["📦 Claquement rapide !", "🍀 Lumière verte scintillante !"],
        "Rare": ["📦 Flash lumineux !", "💎 Brille intensément !", "⚡ Frissons d'excitation !"],
        "Épique": ["📦 Explosion colorée !", "🦄 Arc-en-ciel étincelant !", "🔥 Énergie incroyable !"],
        "Légendaire": ["📦 Le sol tremble !", "🏆 Lumière divine !", "🌟 Tout s’illumine !", "💥 BOUM !"]
    }

    for step in animation_sequences[rarity]:
        await asyncio.sleep(1.2)
        await msg.edit(content=step)

    # ⏸️ petite pause pour laisser la dernière anim visible
    await asyncio.sleep(1.5)

    # Embed final stylé
    style = RARITY_STYLES[rarity]
    embed = discord.Embed(
        title=f"{style['emoji']} Objet {rarity} obtenu !",
        description=f"**{ctx.author.display_name}**, tu viens de tirer :\n\n"
                    f"🎁 **{item}**\n💰 Valeur estimée : **{valeur_fmt} €**",
        color=style["color"]
    )
    embed.set_footer(text=f"Rareté : {rarity}")
    await msg.edit(content=None, embed=embed)



MARKET_FILE = "market.json"


def load_market():
    if not os.path.exists(MARKET_FILE):
        return []
    with open(MARKET_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_market(data):
    with open(MARKET_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


per_page = 10  # nombre d'objets par page


def prepare_pages(shop_items):
    items = list(shop_items.items())
    total_pages = ceil(len(items) / per_page)
    embeds = []
    for i in range(total_pages):
        embed = discord.Embed(title=f"🛒 Boutique - Page {i+1}/{total_pages}",
                              color=discord.Color.blue())
        start = i * per_page
        end = start + per_page
        for item, price in items[start:end]:
            embed.add_field(name=item,
                            value=f"{format_money(price)} €",
                            inline=False)
        embeds.append(embed)
    return embeds


@bot.command()
@commands.cooldown(1, 3600, commands.BucketType.user)
async def work(ctx):
    jobs = {
        "chômeur": 0,
        "livreur": 1600,
        "vendeur": 2000,
        "programmeur": 4500,
        "chauffeur": 1900,
        "serveur": 2300,
        "plombier": 2100,
        "ingénieur logiciel": 3600,
        "médecin": 4900,
        "avocat": 7200,
        "pilote de ligne": 9500,
        "architecte": 4500,
        "chef cuisinier": 3400,
        "designer graphique": 3800,
        "consultant marketing": 3600,
        "développeur IA": 7900,
        "chef de projet": 4800,
        "agent immobilier": 5700,
        "photographe professionnel": 4200,
        "acteur": 8100,
        "musicien": 2600,
        "scientifique": 7800,
        "professeur universitaire": 5000,
        "astronaute": 10000,
        "chef d'entreprise": 9500
    }

    allowed_ids = [1397942510407516170, 511579819960565773]
    if ctx.author.id in allowed_ids:
        jobs.pop("chômeur", None)

    balances = load_balances()
    user_id = str(ctx.author.id)

    job = random.choice(list(jobs.keys()))
    amount = jobs[job]

    balances[user_id] = balances.get(user_id, 0) + amount
    save_balances(balances)

    # Création d'un embed stylé
    embed = discord.Embed(
        title="💼 Travail effectué !",
        description=f"Tu as travaillé comme **{job}** et gagné **{format_money(amount)} €** !",
        color=discord.Color.green()
    )
    embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar.url)
    embed.set_footer(text=f"Nouveau solde : {format_money(balances[user_id])} €")
    embed.timestamp = discord.utils.utcnow()

    await ctx.send(embed=embed)



@work.error
async def work_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        minutes, seconds = divmod(error.retry_after, 60)
        await ctx.send(
            f"⏳ Patiente {int(minutes)} min {int(seconds)} sec avant de pouvoir retravailler, {ctx.author.mention}."
        )


def prepare_pages(items: dict, items_per_page=10):
    embeds = []
    items_list = list(items.items())
    for i in range(0, len(items_list), items_per_page):
        current_items = items_list[i:i + items_per_page]
        embed = discord.Embed(title="🛒 Articles", color=discord.Color.blue())
        desc = ""
        for name, price in current_items:
            desc += f"**{name}** — 💰 {format_money(price)} $\n"
        embed.description = desc
        embed.set_footer(
            text=
            f"Page {i//items_per_page +1} / {(len(items_list)-1)//items_per_page +1}"
        )
        embeds.append(embed)
    if not embeds:
        embed = discord.Embed(
            title="🛒 Articles",
            description="Aucun article dans cette catégorie.",
            color=discord.Color.red())
        embeds.append(embed)
    return embeds


shop_categories = {
    "Technologie & Gaming": {
        "Sony": {
            "PS5 édition limitée": 1200,
            "PS5": 600,
            "PlayStation VR2": 550,
            "Manette DualSense Edge": 200,
            "TV OLED Sony Bravia 65 pouces": 2500,
            "Casque sans fil Sony WH-1000XM5": 350,
            "Enceinte Sony SRS-XB43": 200,
            "Smartwatch Sony Wena 3": 500,
            "Téléphone Sony Xperia 1 V": 1300,
            "Casque gamer Sony INZONE H9": 350,
        },
        "Microsoft": {
            "Xbox Series X": 600,
            "Xbox Series S": 350,
            "Xbox One X": 300,
            "Manette Xbox Elite Series 2": 180,
            "Casque gamer SteelSeries Arctis 7": 150,
            "Casque VR Windows Mixed Reality": 400,
        },
        "Meta": {
            "Meta Quest 3": 550,
            "Meta Quest 3s": 450,
            "Ray-Ban Meta Smart Glasses": 400,
            "Sangle confortable Meta Quest": 60,
            "Lentilles correctrices Meta Quest": 90,
            "Sac de transport Meta Quest": 80,
        },
        "PC & Accessoires": {
            "PC gamer RGB": 3200,
            "Clavier mécanique custom": 700,
            "Carte graphique RTX 5090": 2300,
            "Boîtier PC custom RGB": 900,
            "Microphone pro USB": 400,
            "Webcam 4K HDR": 350,
            "Tapis de souris XXL": 30,
            "Lampe LED gaming": 100,
            "Setup streaming complet": 4500,
            "Chaise gaming ergonomique": 800,
            "Support smartphone RGB": 70,
            "SSD NVMe 2To": 250,
            "Moniteur 4K 144Hz": 600,
            "Casque gaming Logitech G Pro X": 150,
            "Carte mère ASUS ROG": 400,
            "Processeur Intel i9-13900K": 750,
            "Refroidisseur liquide Corsair": 200,
            "Alimentation 850W modulaire": 180,
            "Mémoire RAM 32Go DDR5": 350,
        },
        "Nintendo": {
            "Nintendo Switch OLED": 350,
            "Game Boy édition rétro": 250,
            "Figurine collector Mario": 250,
            "Affiche rétro Mario": 200,
            "Affiche rétro Zelda": 200,
            "Accessoires Joy-Con Nintendo": 40,
            "Manette Pro Nintendo Switch": 70,
            "Coque Nintendo Switch": 20,
            "Casque gaming officiel Nintendo": 80,
            "Tapis de souris Mario": 25,
        },
        "Apple": {
            "iPhone 16 Pro Max": 1300,
            "iPhone 16": 1100,
            "iPhone SE 4": 450,
            "iPad Pro": 3800,
            "iPad Air": 700,
            "iMac 24 pouces M1": 2000,
            "Mac Mini M2": 1000,
            "MacBook Pro 16 pouces M2 Max": 3500,
            "Apple Watch Series 9": 500,
            "AirPods Pro 2": 300,
            "AirPods Max": 600,
            "Apple TV 4K": 200,
            "Apple vision pro":2000,
        },
        "Samsung": {
            "Samsung Galaxy S25 Ultra": 1200,
            "Samsung Galaxy Tab S10 Ultra": 1500,
            "Chargeur sans fil rapide": 60,
            "Écouteurs Galaxy Buds Pro": 200,
            "Smartwatch Galaxy Watch 6": 400,
            "TV Samsung QLED 75 pouces": 3000,
            "Samsung Galaxy Z Fold 5": 1800,
            "Samsung Galaxy Watch 5 Pro": 500,
            "Barre de son Samsung HW-Q900B": 800,
            "Moniteur Samsung Odyssey G7": 700,
            "Clavier Samsung Smart Keyboard": 150,
            "Samsung Portable SSD T7": 200,
            "Casque Bluetooth Samsung": 150,
            "Caméra de sécurité Samsung": 100,
            "Samsung Galaxy A54": 400,
            "Samsung Galaxy Buds Live": 150,
        },
        "Google": {
            "Google Pixel 9 Pro": 900,
            "Google Nest Hub Max": 250,
            "Chromecast avec Google TV": 70,
            "Google Pixelbook Go": 1200,
            "Google Nest Audio": 100,
            "Google Pixel 8": 700,
            "Google Chromecast Ultra": 80,
            "Google Pixel Buds Pro": 200,
            "Google Wifi 3-pack": 250,
            "Google Nest Cam": 180,
            "Clavier Google Pixel Slate": 150,
            "Google Daydream View": 150,
            "Google Stadia Controller": 70,
            "Support Google Nest": 40,
            "Google Home Mini": 50,
            "Google Pixel Stand": 80,
            "Pixel Slate Pen": 100,
            "Google Titan Security Key": 60,
            "Pixelbook Pen": 130,
        },
        "Audio": {
            "Casque audio Hi-Fi Sony WH-1000XM5": 600,
            "Écouteurs Bose QuietComfort": 280,
            "Batterie externe 20000mAh": 80,
            "Enceinte Bluetooth JBL Charge 5": 200,
            "Amplificateur casque FiiO K5 Pro": 220,
            "Casque gaming SteelSeries Arctis 7": 150,
            "Microphone Blue Yeti": 140,
            "Barre de son Sonos Beam": 500,
            "Enceinte Bose Home Speaker 500": 400,
            "DAC AudioQuest DragonFly": 300,
            "Casque audiophile Sennheiser HD 660S": 500,
            "Écouteurs Shure SE215": 100,
            "Station d’accueil audio USB": 250,
            "Casque Bluetooth Jabra Elite 85h": 300,
            "Microphone Rode NT-USB": 150,
            "Enceinte Marshall Stanmore II": 350,
            "Récepteur Bluetooth TaoTronics": 40,
            "Pied micro professionnel": 80,
            "Table de mixage Behringer Xenyx": 350,
        },
        "Smartphones Gaming": {
            "Smartphone gaming ASUS ROG Phone 7": 1500,
            "Xiaomi Black Shark 6 Pro": 800,
            "Lenovo Legion Phone Duel 2": 950,
            "Nubia RedMagic 7S Pro": 850,
            "ASUS ROG Phone 6": 1200,
            "Xiaomi Black Shark 5 Pro": 700,
            "Lenovo Legion Phone Duel": 850,
            "Nubia RedMagic 6 Pro": 750,
            "ASUS ROG Phone 5s": 1000,
            "Xiaomi Poco F4 GT": 650,
            "Lenovo Legion 2 Pro": 900,
            "Nubia RedMagic 5G": 700,
            "Black Shark 4 Pro": 600,
            "ASUS ROG Phone 3": 800,
            "Lenovo Legion Phone 3": 650,
            "Nubia RedMagic 3S": 600,
            "ASUS ROG Phone 2": 700,
            "Xiaomi Black Shark 2": 550,
            "Lenovo Legion Phone": 600,
            "Nubia RedMagic Mars": 500,
        },
        "jeux": {
            "Minecraft": 30,
            "GTA 5": 30,
            "Mario Kart World": 70,
            "FC 25": 60,
            "Forza Horizon 5": 70,
            "Call of Duty Modern Warfare II": 70,
            "The Legend of Zelda: Tears of the Kingdom": 70,
            "Cyberpunk 2077": 50,
            "Elden Ring": 60,
            "League of Legends (skins)": 15,
            "Assassin's Creed Valhalla": 50,
            "Red Dead Redemption 2": 60,
            "Animal Crossing New Horizons": 60,
            "Horizon Forbidden West": 70,
            "Super Smash Bros Ultimate": 60,
            "God of War Ragnarök": 70,
            "Marvel's Spider-Man 2": 70,
            "The Witcher 3: Wild Hunt": 40,
            "Sekiro: Shadows Die Twice": 60,
            "Gran Turismo 7": 70,
            "Street Fighter 6": 60,
            "Resident Evil 4 Remake": 60,
            "Metroid Dread": 60,
            "Final Fantasy XVI": 70,
            "Ghost of Tsushima": 60,
            "Diablo IV": 70,
            "Starfield": 70,
            "Pokémon Écarlate": 60,
            "Pokémon Violet": 60,
            "Splatoon 3": 60
        }
    },
    "Vêtements & Équipements": {
        "Super Vêtements Légendaire": {
            "Costume de trader légendaire": 400000000,
            "lunettes d'expert légendaire": 200000000,
            "chaussure de salopard légendaire": 200000000,
            "Pentalon Mobcraft légendaire": 200000000,
        },
        "Super Vêtements Mythique": {
            "Costume de trader mythique": 40000000,
            "lunettes d'expert mythique": 20000000,
            "chaussure de salopard mythique": 20000000,
            "Pentalon Mobcraft mythique": 20000000,
        },
        "Super Vêtements Rare": {
            "Costume de trader rare": 400000,
            "lunettes d'expert rare": 200000,
            "chaussure de salopard rare": 200000,
            "Pentalon Mobcraft rare": 200000,
        },
        "Super Vêtements Commun": {
            "Costume de trader commun": 40000,
            "lunettes d'expert commun": 20000,
            "chaussure de salopard commun": 20000,
            "Pentalon Mobcraft commun": 20000,
        },
        "Maillots de foot": {
            "maillot du Tigre FC": 100,
            "maillot du FC Renard": 100,
            "maillot du FC Parrot": 100,
            "maillot du FC Calamar": 100,
            "maillot du FC Dragão": 100,
            "maillot du FC Noyé": 100,
            "maillot du Sporting Axolotl": 100,
            "maillot du FC Azur": 100,
            "maillot du FC Goat": 100,
            "maillot du Ghast city FC": 100,
            "maillot du Pig FC": 100,
            "maillot de l'Olympique Mouton": 100,
            "maillot du FC Dauphin": 100,
        }
    },
    "Voitures": {
        "Porsche": {
            "Porsche 911 GT2 RS": 289175,
            "Porsche 911 GT3 RS": 248000,
            "Porsche 918 Spyder": 775000,
            "Porsche Taycan": 106000,
            "Porsche Panamera": 119000,
            "Porsche Macan": 58000,
            "Porsche Cayenne": 67000,
            "Porsche 911 Carrera": 101200,
            "Porsche 911 Turbo S": 204000,
            "Porsche Boxster": 62000,
            "Porsche Cayman": 70000,
            "Porsche 911 Targa 4": 120000,
            "Porsche 911 Carrera S": 115000,
            "Porsche 911 GT3": 180000,
            "Porsche 911 Carrera 4S": 120000,
            "Porsche Panamera Turbo": 160000,
            "Porsche Macan Turbo": 68000,
            "Porsche Cayenne Turbo": 120000,
            "Porsche 911 Speedster": 280000,
            "Porsche 911 Carrera GTS": 135000,
        },
        "Ferrari": {
            "Ferrari LaFerrari": 4000000,
            "Ferrari Enzo": 5000000,
            "Ferrari 812 Superfast": 569974,
            "Ferrari 458 Italia": 510000,
            "Ferrari 458 Spécial": 415000,
            "Ferrari FXX K": 2400000,
            "Ferrari 488 GTB": 235000,
            "Ferrari F12 Berlinetta": 271786,
            "Ferrari 488 Challenge Evo": 260000,
            "Ferrari SF90": 440000,
            "Ferrari F80": 3600000,
            "Ferrari 488 Pista": 410000,
            "Ferrari F12 TDF": 500000,
            "Ferrari Roma": 250000,
            "Ferrari California T": 210000,
            "Ferrari Portofino": 215000,
            "Ferrari GTC4Lusso": 300000,
            "Ferrari 599 GTO": 350000,
            "Ferrari Enzo": 3000000,
            "Ferrari 330 P4": 10000000,
            "Ferrari Testarossa": 150000,
            "Ferrari 360 Modena": 180000,
        },
        "Lamborghini": {
            "Lamborghini Revuelto": 500000,
            "Lamborghini Veneno": 10000000,
            "Lamborghini Urus": 215000,
            "Lamborghini Sian FKP57": 3700000,
            "Lamborghini Gallardo": 210000,
            "Lamborghini Sesto Elemento": 2700000,
            "Lamborghini Murcielago": 180000,
            "Lamborghini Aventador": 380000,
            "Lamborghini Centenario": 2100000,
            "Lamborghini Huracán": 260000,
            "Lamborghini Diablo": 250000,
            "Lamborghini Countach": 450000,
            "Lamborghini Espada": 180000,
            "Lamborghini Miura": 2000000,
            "Lamborghini Reventón": 1700000,
            "Lamborghini Estoque": 230000,
            "Lamborghini Urus Performante": 250000,
            "Lamborghini Huracán EVO": 290000,
            "Lamborghini Sián Roadster": 4000000,
            "Lamborghini Huracán STO": 320000,
            "Lamborghini Aventador SVJ": 4500000,
            "Lamborghini Urus Performante": 250000,
        },
        "Bugatti": {
            "Bugatti Bolide": 4150000,
            "Bugatti Divo": 5000000,
            "Bugatti Chiron": 3200000,
            "Bugatti Veyron": 1500000,
            "Bugatti Tourbillon": 3800000,
            "Bugatti Mistral": 5000000,
            "Bugatti Centodieci": 8000000,
            "Bugatti La Voiture Noire": 15900000,
            "Bugatti Veyron": 1500000,
            "Bugatti EB110": 1000000,
            "Bugatti Type 57SC Atlantic": 30000000,
            "Bugatti Type 41 Royale": 10000000,
        },
        "Koenigsegg": {
            "Koenigsegg Regera": 3430000,
            "Koenigsegg Agera": 3100000,
            "Koenigsegg Jesko": 2500000,
            "Koenigsegg One:1": 2800000,
            "Koenigsegg CCX": 700000,
            "Koenigsegg Gemera": 1700000,
            "Koenigsegg CC8S": 1500000,
            "Koenigsegg CCXR": 2000000,
            "Koenigsegg CCXR Trevita": 2500000,
            "Koenigsegg Agera RS": 3500000,
        },
        "Audi": {
            "Audi RS6 GT": 192500,
            "Audi RSQ8": 191550,
            "Audi RS3": 75000,
            "Audi M4": 123000,
            "Audi R8": 260000,
            "Audi R8 GT2": 300000,
            "Audi ABT R8 XGT": 600000,
            "Audi A4": 58000,
            "Audi RS7 Sportback": 157000,
            "Audi R8 V10 Plus": 200000,
            "Audi RS4 Avant": 100000,
            "Audi RS5": 120000,
            "Audi RS7": 180000,
            "Audi RS6 Avant": 160000,
            "Audi RSQ8 Sportback": 190000,
            "Audi RS3 Sportback": 80000,
            "Audi RS4": 110000,
            "Audi RS5 Sportback": 130000,
            "Audi RS6": 170000,
            "Audi RSQ3": 90000,
            "Audi RSQ5": 140000,
            "Audi RSQ7": 200000,
        },
        "BMW": {
            "BMW M4 G82": 194100,
            "BMW IX M60": 100000,
            "BMW Série 5 G30": 58000,
            "BMW I8 Tuning": 165000,
            "BMW M5": 160000,
            "BMW E-tron GT": 128250,
            "BMW i4": 70000,
            "BMW X5 M": 110000,
            "BMW X6 M": 115000,
            "BMW M3 G80": 70000,
            "BMW Z4 M40i": 70000,
            "BMW 7 Series": 85000,
            "BMW X7": 100000,
            "BMW 330i": 45000,
            "BMW M2 Competition": 60000,
            "BMW M8 Competition": 145000,
            "BMW X3 M": 67000,
            "BMW iX": 105000,
            "BMW M340i": 55000,
            "BMW 4 Series Coupe": 50000,
            "BMW 8 Series": 120000,
            "BMW X1": 40000,
            "BMW X4": 50000,
        },
        "Mercedes": {
            "Mercedes AMG GT": 134950,
            "Mercedes-Benz E 220": 94000,
            "Mercedes-AMG ONE": 2275000,
            "Mercedes AVTR": 1250000,
            "Mercedes-Benz SLR McLaren": 300000,
            "Formule 1 Mercedes": 1000000,
            "Mercedes G-Class AMG": 160000,
            "Mercedes C63 AMG": 80000,
            "Mercedes S-Class Maybach": 180000,
            "Mercedes CLA AMG": 56000,
            "Mercedes A45 AMG": 60000,
            "Mercedes GLS": 120000,
            "Mercedes E63 AMG": 115000,
            "Mercedes GLE Coupe": 90000,
            "Mercedes SL AMG": 135000,
            "Mercedes EQS": 150000,
            "Mercedes GLC AMG": 65000,
            "Mercedes SLC AMG": 65000,
            "Mercedes EQA": 56000,
            "Mercedes EQC": 70000,
        },
        "Chevrolet": {
            "Chevrolet Corvette": 132000,
            "Chevrolet Corvette C8 Stingray": 250000,
            "Chevrolet Camaro GT": 50000,
            "Chevrolet Silverado": 40000,
            "Chevrolet Tahoe": 49000,
            "Chevrolet Suburban": 60000,
            "Chevrolet Traverse": 35000,
            "Chevrolet Bolt EV": 37000,
            "Chevrolet Malibu": 24000,
            "Chevrolet Colorado": 32000,
            "Chevrolet Impala": 31000,
            "Chevrolet Sonic": 17000,
            "Chevrolet Equinox": 29000,
            "Chevrolet Trailblazer": 25000,
            "Chevrolet Blazer": 42000,
            "Chevrolet Spark": 14000,
            "Chevrolet Cruze": 23000,
            "Chevrolet Tahoe RST": 56000,
            "Chevrolet Camaro ZL1": 65000,
            "Chevrolet Corvette Z06": 85000,
        },
        "Ford": {
            "Ford Mustang": 59300,
            "Ford GT": 400000,
            "Ford F-150": 30000,
            "Ford Explorer": 40000,
            "Ford Bronco": 35000,
            "Ford Ranger": 28000,
            "Ford Focus": 22000,
            "Ford Fiesta": 15000,
            "Ford Escape": 25000,
            "Ford Edge": 32000,
            "Ford Flex": 35000,
            "Ford EcoSport": 20000,
            "Ford Maverick": 22000,
            "Ford Transit": 35000,
            "Ford Fusion": 24000,
            "Ford Expedition": 54000,
            "Ford Taurus": 29000,
            "Ford Shelby GT500": 73000,
            "Ford Mustang Mach-E": 52000,
            "Ford C-Max": 25000,
        },
        "McLaren": {
            "McLaren 750S": 280000,
            "McLaren P1": 1500000,
            "McLaren Senna": 930000,
            "McLaren 720S": 250000,
            "McLaren Speedtail": 2100000,
            "McLaren Artura": 225000,
            "McLaren 570S": 190000,
            "McLaren 600LT": 210000,
            "McLaren 765LT": 300000,
            "McLaren GT": 210000,
        },
        "Aston Martin": {
            "Aston Martin DBS": 274995,
            "Aston Martin Valkyrie": 2500000,
            "Aston Martin Valhalla": 860000,
            "Aston Martin Vanquish": 400000,
            "Aston Martin Vantage": 260000,
            "Aston Martin Vulcan": 1500000,
            "Aston Martin DB11": 200000,
            "Aston Martin Rapide": 210000,
            "Aston Martin Cygnet": 40000,
            "Aston Martin Lagonda": 200000,
        },
        "Autres": {
            "Tofaş Yelkenci": 5000,
            "Reliant Supervan III": 20000,
            "Pagani Zonda R": 1746000,
            "Alpine A110": 65000,
            "Lexus ES": 60200,
            "Rolls-Royce Droptail": 23000000,
            "Daytona SP3": 1968000,
            "GTR R35": 70000,
            "Rimac Nevera": 2000000,
            "Tesla Model S Plaid": 130000,
            "Lotus Evora": 96000,
            "Bentley Continental GT": 210000,
            "Jaguar F-Type": 75000,
            "Maserati MC20": 210000,
            "Pagani Huayra": 2600000,
            "Koenigsegg Gemera": 1700000,
            "DeLorean DMC-12": 120000,
            "Caterham Seven": 65000,
            "Hennessey Venom F5": 2500000,
            "Saleen S7": 600000,
        }
    },
    "Immobilier": {
        "Villas & Maisons": {
            "Villa Les Cèdres (Côte d’Azur)": 380000000,
            "Antilia (Mumbai, 27 étages)": 2100000000,
            "Villa Leopolda (France)": 500000000,
            "The One (Bel Air, LA)": 295000000,
            "Manoir sur Central Park (NYC)": 75000000,
            "Penthouse One Hyde Park (Londres)": 225000000,
            "Villa en Provence avec piscine": 1600000,
            "Manoir hanté (à rénover)": 350000,
            "maison à Dubaï": 2100000,
            "Maison en bois en Norvège": 480000,
            "Villa au bord du lac (Suisse)": 1300000,
            "Château médiéval (France)": 3800000,
            "Palais Buckingham (Londres)": 5000000000,
            "Palais de Versailles (France, valeur estimée)": 2000000000,
            "Villa Aurora (Rome)": 480000000,
            "Fairfield Pond (NY, USA)": 248000000,
            "Maison à Beverly Hills avec piste d'atterrissage": 320000000,
            "Villa à Miami avec yacht privé inclus": 180000000,
            "Penthouse à Monaco avec toboggan piscine": 310000000,
            "Maison flottante à Dubaï": 12000000,
            "Villa éco-responsable à Bali": 2900000,
            "Loft industriel à Brooklyn": 3200000,
            "Maison de montagne à Aspen": 6700000,
            "Villa japonaise traditionnelle (Kyoto)": 2100000,
            "Villa Art Déco à Los Angeles": 8500000,
            "Villa high-tech à Séoul": 3800000,
            "Riad de luxe à Marrakech": 2100000,
            "Cabane design au Canada": 630000,
            "Villa futuriste en Californie": 12000000,
            "Appartement haussmannien à Paris": 4100000,
            "Maison troglodyte modernisée (Turquie)": 1400000,
            "Chalet en bois aux Alpes": 1900000,
            "Villa sur l’île de Santorin": 2700000,
            "Villa suspendue sur falaises (Mexique)": 3300000,
            "Maison à toit végétal en Suède": 920000,
            "Maison en verre en Finlande": 770000,
            "Maison container ultra moderne": 510000,
            "Maison de campagne avec jardin": 320000,
            "Maison mitoyenne en banlieue": 270000,
            "Pavillon familial 4 chambres": 360000,
            "Villa moderne plain-pied": 450000,
            "Maison traditionnelle avec cheminée": 390000,
            "Villa avec piscine et garage": 620000,
            "Petite maison de ville rénovée": 310000,
            "Maison en lotissement calme": 340000,
            "Villa néo-provençale": 540000,
            "Maison bord de mer (Bretagne)": 570000,
            "Maison avec combles aménagés": 410000,
            "Villa 3 chambres avec terrasse": 490000,
            "Maison ancienne rénovée (centre-ville)": 430000,
            "Maison avec grand terrain": 600000,
            "Maison de plain-pied avec véranda": 380000,
            "Maison à étage avec balcon": 420000,
            "Maison jumelée avec petit jardin": 295000,
            "Maison bois scandinave": 460000,
            "Maison ossature bois écolo": 510000,
            "Maison de lotissement récent": 370000,
            "Maison 2 chambres cosy": 250000,
            "Maison de ville avec garage": 330000,
            "Maison style méditerranéen": 520000,
            "Maison avec vue sur montagne": 590000,
            "Maison avec atelier indépendant": 480000,
        }
    },
    "Bateaux & Yachts": {
        "Yachts": {
            "History Supreme (yacht en or)": 4100000000,
            "Eclipse (Roman Abramovich)": 1300000000,
            "Azzam (180m, yacht royal)": 600000000,
            "Flying Fox (136m)": 400000000,
            "Yatch Lamborghini 63": 4000000,
            "Yacht 30m (avec jacuzzi)": 4200000,
        },
        "Sous-marins": {
            "Sous-marin personnel de luxe": 35000000,
            "Sous-marin personnel": 3200000,
        },
        "Catamarans": {
            "Catamaran Sunreef 80 Power": 8000000,
            "Catamaran 12m": 690000,
        },
        "Autres": {
            "Voilier de luxe": 850000,
            "Jet ski Yamaha": 14000,
            "Bateau de pêche customisé": 75000,
        }
    },
    "Jets privés & Avions VIP": {
        "Très gros porteurs VIP": {
            "Airbus A380 VIP (Prince saoudien)": 500000000,
            "Boeing 747-8 VIP (Air Force One)": 430000000,
            "Boeing 747-8 VIP": 430000000,
            "Boeing 777X VIP": 400000000,
            "Airbus A350-1000": 366000000,
            "Boeing 787 Dreamliner VIP": 325000000,
            "Airbus A340-600": 300000000,
            "Airbus A330neo": 270000000
        },
        "Jets privés long-courriers": {
            "Jet privé Bombardier Global 8000": 78000000,
            "Bombardier Global 8000": 78000000,
            "Gulfstream G700": 75000000,
            "Dassault Falcon 10X": 75000000,
            "Jet privé Gulfstream G650": 65000000
        },
        "Jets privés légers": {
            "Boeing 737 BBJ MAX": 110000000,
            "Cessna Citation Longitude": 27000000,
            "Pilatus PC-24": 11000000
        }
    },
    "Avions Militaires & Autres": {
        "Hydravions & Vintage": {
            "Hydravion militaire reconditionné": 1200000,
            "Hydravion vintage": 350000
        },
        "Militaires & Collection": {
            "Avion de chasse désarmé (collection)": 1900000,
            "Drone militaire reconditionné": 120000
        },
        "Loisirs & Autres": {
            "Montgolfière personnalisée": 85000,
            "Planeur silencieux": 18000
        }
    },
    "Motos": {
        "Ducati": {
            "Ducati Panigale V4 R": 45000,
            "Ducati Panigale V4 SP": 40000,
            "Ducati Multistrada V4": 12000,
            "Ducati Diavel 1260": 15000,
            "Ducati Monster 1200": 13000,
            "Ducati Streetfighter V4": 18000,
        },
        "Harley-Davidson": {
            "Harley-Davidson CVO Limited": 50000,
            "Harley-Davidson Fat Boy": 21000,
            "Harley-Davidson Street 750": 12000,
            "Harley-Davidson Sportster": 10000,
            "Harley-Davidson Softail": 15000,
        },
        "Yamaha": {
            "Yamaha R1M": 26000,
            "Yamaha YZF-R1": 21000,
            "Yamaha MT-07": 7000,
            "Yamaha Tracer 9": 6000,
            "Yamaha Tricity 125": 4000,
            "Yamaha WR250R": 5000,
        },
        "Kawasaki": {
            "Kawasaki Ninja H2R": 55000,
            "Kawasaki Z H2": 16000,
            "KTM 1290 Super Duke R": 18000,
            "KTM 1290 Super Adventure": 20000,
            "Kawasaki Versys 1000": 12000,
            "Kawasaki Z900": 10000,
            "Kawasaki ZX 10R": 30000
        },
        "BMW": {
            "BMW HP4 Race": 78000,
            "BMW S1000RR": 21000,
            "BMW R 1250 GS": 10000,
            "BMW R 1250 GS Adventure": 12000,
            "BMW R 1250 RT": 15000,
            "BMW R 1250 R": 18000,
            "BMW R 1250 GS Classic": 13000,
            "BMW R 1250 GS Adventure Classic": 15000,
            "BMW S1000RR": 21000,
        },
        "MV Agusta": {
            "MV Agusta F4 Claudio": 70000,
            "MV Agusta Brutale 1000 Serie Oro": 90000,
            "MV Agusta F3 1000": 12000,
            "MV Agusta F3 675": 10000,
            "MV Agusta F3 800": 11000,
        },
        "Autres Marques": {
            "Dodge Tomahawk": 550000,
            "Neiman Marcus Limited Edition Fighter": 110000,
            "Confederate FA-13 Combat Bomber": 155000,
            "Lightning LS-218 (électrique)": 38000,
            "Honda RC213V-S": 184000,
            "Aprilia RSV4 1100 Factory": 26000,
            "Suzuki Hayabusa": 18000,
            "Triumph Rocket 3": 24000,
            "Indian Chief Vintage": 28000,
            "Zero SR/F (électrique)": 20000,
            "Bimota Tesi H2": 130000,
            "Suzuki GSX-R1000": 17000,
            "Honda CBR1000RR-R Fireblade": 28000,
            "Aprilia Tuono V4 1100": 18000,
            "Triumph Street Triple RS": 13000,
            "Indian Scout Bobber": 14000,
            "Zero SR/S (électrique)": 22000,
            "Moto Guzzi V85 TT": 15000,
            "Royal Enfield Himalayan": 5000,
            "Norton Commando 961": 19000,
            "Bajaj Dominar 400": 4000,
            "KTM Duke 390": 4500,
            "Husqvarna Svartpilen 401": 6500,
        }
    },
    "Objets de collection & Luxe": {
        "Montres & Bijoux": {
            "Montre Rolex Submariner": 15000,
            "Montre Patek Philippe Nautilus": 85000,
            "Montre Audemars Piguet Royal Oak": 40000,
            "Montre Omega Speedmaster": 9000,
            "Montre TAG Heuer Carrera": 5500,
            "Montre Cartier Tank": 10000,
            "Rolex Day-Date President": 40000,
            "Montre Jaeger-LeCoultre Reverso": 12000,
            "Montre Breitling Navitimer": 8500,
            "Montre IWC Portugieser": 14000,
            "Montre Hublot Big Bang": 25000,
            "Montre Panerai Luminor": 9000,
            "Montre Vacheron Constantin Overseas": 38000,
            "Montre Blancpain Fifty Fathoms": 16000,
            "Montre Tudor Black Bay": 4500,
            "Montre Zenith El Primero": 8000,
            "Montre Longines Master Collection": 3000,
            "Montre Bell & Ross BR 03": 4200,
            "Montre Girard-Perregaux Laureato": 13000,
            "Montre Glashütte Original Senator": 15000,
            "Montre Breguet Classique": 30000,
            "Montre Franck Muller Vanguard": 20000,
            "Montre Raymond Weil Freelancer": 2500,
            "Montre Oris Aquis": 2500,
            "Montre Seiko Presage": 1200,
            "Montre Casio G-Shock MR-G": 3000,
            "Bague en diamant": 12000,
            "Collier en or": 8000,
            "Bracelet en argent": 4000,
            "Boucles d'oreilles en or blanc": 5000,
            "Collier Tiffany & Co.": 12000,
            "Bague en saphir": 6000,
            "Broche vintage en or": 3500,
        },
        "Œuvres d'art": {
            # Ultra prestigieux / légendaires
            "Peinture originale de Picasso (authentifiée)": 120000000,
            "Sculpture en bronze de Rodin": 8500000,
            "Toile de Van Gogh (réplique certifiée rare)": 4000000,
            "Photographie d'art de Ansel Adams (édition limitée)": 500000,
            "Œuvre numérique NFT d'artiste célèbre": 350000,
            "Tableau impressionniste de Monet": 9000000,
            "Sculpture contemporaine de Jeff Koons": 2500000,
            "Gravure ancienne de Rembrandt": 550000,
            "Œuvre d'art abstrait de Kandinsky": 1200000,
            "Lithographie originale de Matisse": 850000,
            "Céramique d'artiste célèbre (exposition)": 650000,
            
            # Oeuvres plus abordables mais toujours prisées
            "Peinture moderne d'artiste émergent": 180000,
            "Photographie artistique en édition limitée": 95000,
            "Sculpture en verre soufflé": 85000,
            "Dessin au fusain d'artiste reconnu": 65000,
            "Gravure contemporaine": 55000,
            "Œuvre d'art abstrait locale": 48000,
            "Lithographie numérotée": 37000,
            "Céramique artisanale d'artiste local": 22000,
        },
        "Accessoires Mode": {
            "Sac à main Chanel": 8000,
            "Sac Hermès Birkin": 120000,
            "Lunettes de soleil Gucci": 500,
            "Chaussures Louboutin": 1200,
            "Écharpe en soie Hermès": 900,
            "Montre bracelet Louis Vuitton": 7500,
            "Portefeuille Prada": 800,
            "Ceinture Gucci en cuir": 600,
            "Chapeau en feutre vintage": 400,
            "Parfum Dior Sauvage": 120,
            "Chaussures Gucci en cuir": 1400,
            "Ceinture en cuir Hermès": 900,
            "Lunettes de soleil Ray-Ban Aviator": 180,
            "Blouson en cuir Saint Laurent": 3000,
            "Sacoche en cuir Prada": 1500,
            "Cravate en soie Hugo Boss": 200,
            "Portefeuille Montblanc": 650,
            "Bague en acier inoxydable": 350,
            "Coffret rasage classique": 120,
            "Chapeau Fedora en laine": 400,
            "Écharpe en cachemire": 600,
            "Bracelet en cuir tressé": 180,
            "Parapluie automatique haut de gamme": 150,
        },
        "Objets de collections": {
            # Très très chers et ultra rares
            "Carte Pokémon Pikachu Illustrator (ultra rare)": 6000000,
            "Manuscrit original de Léonard de Vinci": 15000000,
            "Montre Rolex Submariner appartenant à Paul Newman": 1800000,
            "Sabre laser utilisé dans Star Wars Episode IV": 750000,
            "Guitare Fender Stratocaster signée par Jimi Hendrix": 1250000,
            "Timbre britannique Penny Black (1840)": 850000,
            "Chaussures Air Jordan 1 portées par Michael Jordan": 650000,
            "Balle de baseball signée par Babe Ruth": 400000,
            "Affiche de film Titanic signée par tout le casting": 85000,
            
            # Moyennement chers
            "Livre ancien relié en or (XVIIe siècle)": 120000,
            "Maquette Bugatti Type 57SC Atlantic plaquée or": 150000,
            "Vinyle de Michael Jackson - Thriller édition test press": 95000,
            "Casque de Stormtrooper original (Star Wars)": 250000,
            "Panneau publicitaire Coca-Cola des années 1920": 32000,
            
            # Plus accessibles
            "Console Nintendo Game Boy scellée (édition 1989)": 45000,
            "Timbres rares": 600,
            "Accessoire de cinéma authentique": 1800,
            "Instrument de musique ancien": 7500,
            "Plaque publicitaire vintage": 250,
            "Maquette de voiture ancienne": 900,
            "Jeu vidéo collector": 400,
            "Vinyle collector": 350,
            "Poster vintage film culte": 80,
            "Figurine Star Wars édition limitée": 150,
            "Cartes Pokémon rares": 1200,
            "Livre rare édition première": 1200,
        }
    },
    "Divers & Quotidien": {
        "Maison": {
            "Robot aspirateur": 300,
            "Machine à café": 150,
            "Lustre design": 600,
            "Lampadaire LED": 100,
            "Plante verte décorative": 40,
            "Diffuseur d'huiles essentielles": 80,
        },
        "Cuisine": {
            "Batterie de cuisine inox": 200,
            "Set de couteaux professionnels": 350,
            "Mixeur blender": 120,
            "Grille-pain": 60,
        },
        "Bureau": {
            "Chaise ergonomique": 220,
            "Lampe de bureau LED": 70,
            "Clavier sans fil": 80,
            "Souris gaming": 100,
        },
        "Loisirs": {
            "Jeu de société stratégique": 50,
            "Livre best-seller": 30,
            "Kit de modélisme": 90,
            "Instrument de musique": 450,
            "Drone de loisir": 350,
        },
        "Sport": {
            "Vélo de course": 900,
            "Tapis de yoga": 60,
            "Equipement fitness": 150,
        }
    }
}

shop_items = {}
for category, subcats in shop_categories.items():
    for subcat, products in subcats.items():
        shop_items.update(products)

class ItemsView(discord.ui.View):

    def __init__(self, items_dict, author_id):
        super().__init__(timeout=120)
        self.pages = prepare_pages(items_dict)
        self.page = 0
        self.author_id = author_id

        # Si 1 page max, désactive les boutons
        if len(self.pages) <= 1:
            self.prev_button.disabled = True
            self.next_button.disabled = True

    async def interaction_check(self,
                                interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.author_id:
            await interaction.response.send_message(
                "Ce n'est pas votre boutique.", ephemeral=True)
            return False
        return True

    @discord.ui.button(label="◀️", style=discord.ButtonStyle.secondary)
    async def prev_button(self, interaction: discord.Interaction,
                          button: discord.ui.Button):
        if self.page > 0:
            self.page -= 1
            await interaction.response.edit_message(
                embed=self.pages[self.page], view=self)

    @discord.ui.button(label="▶️", style=discord.ButtonStyle.secondary)
    async def next_button(self, interaction: discord.Interaction,
                          button: discord.ui.Button):
        if self.page < len(self.pages) - 1:
            self.page += 1
            await interaction.response.edit_message(
                embed=self.pages[self.page], view=self)


class SubCategoryView(discord.ui.View):

    def __init__(self, subcat_dict, author_id):
        super().__init__(timeout=120)
        self.subcat_dict = subcat_dict
        self.author_id = author_id
        for name, items in subcat_dict.items():
            self.add_item(self.SubCategoryButton(name, items))

    async def interaction_check(self,
                                interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.author_id:
            await interaction.response.send_message(
                "Ce n'est pas votre boutique.", ephemeral=True)
            return False
        return True

    class SubCategoryButton(discord.ui.Button):

        def __init__(self, name, items):
            super().__init__(label=name, style=discord.ButtonStyle.primary)
            self.name = name
            self.items = items

        async def callback(self, interaction: discord.Interaction):
            # items ici = dict d'articles nom: prix
            view = ItemsView(self.items, interaction.user.id)
            await interaction.response.edit_message(embed=view.pages[0],
                                                    view=view)


class CategoryView(discord.ui.View):

    def __init__(self, categories_dict, author_id):
        super().__init__(timeout=120)
        self.categories_dict = categories_dict
        self.author_id = author_id
        for name, subcat in categories_dict.items():
            self.add_item(self.CategoryButton(name, subcat))

    async def interaction_check(self,
                                interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.author_id:
            await interaction.response.send_message(
                "Ce n'est pas votre boutique.", ephemeral=True)
            return False
        return True

    class CategoryButton(discord.ui.Button):

        def __init__(self, name, subcat):
            super().__init__(label=name, style=discord.ButtonStyle.primary)
            self.name = name
            self.subcat = subcat

        async def callback(self, interaction: discord.Interaction):
            # subcat ici = dict sous-catégories
            view = SubCategoryView(self.subcat, interaction.user.id)
            embed = discord.Embed(
                title=f"🗂️ {self.name} - Sous-catégories",
                description="Choisis une sous-catégorie ci-dessous :",
                color=discord.Color.green())
            await interaction.response.edit_message(embed=embed, view=view)


@bot.command()
async def shop(ctx):
    embed = discord.Embed(title="🛍️ Boutique",
                          description="Choisis une catégorie ci-dessous :",
                          color=discord.Color.green())
    view = CategoryView(shop_categories, ctx.author.id)
    await ctx.send(embed=embed, view=view)




def prepare_market_pages(market_list, items_per_page=10):
    pages = []
    total_pages = (len(market_list) - 1) // items_per_page + 1

    colors = [discord.Color.blue(), discord.Color.green(), discord.Color.purple()]
    for i in range(0, len(market_list), items_per_page):
        chunk = market_list[i:i + items_per_page]
        color = colors[(i // items_per_page) % len(colors)]

        embed = Embed(title="🏪 Marché des joueurs", color=color)

        for offer in chunk:
            embed.add_field(
                name=f"🆔 {offer['id']} — {offer['objet']}",
                value=(
                    f"👤 Vendeur : **{offer['vendeur']}**\n"
                    f"💰 Prix : **{format_money(offer['prix'])} €**"
                ),
                inline=False
            )

        current_page = (i // items_per_page) + 1
        embed.set_footer(text=f"Page {current_page}/{total_pages} • {len(market_list)} offres au total")
        pages.append(embed)

    return pages



class BuyModal(discord.ui.Modal, title="🛒 Acheter un objet"):
    offer_id = discord.ui.TextInput(
        label="ID de l'offre",
        placeholder="Exemple : 3",
        required=True
    )

    def __init__(self, buyer_id: int):
        super().__init__()
        self.buyer_id = buyer_id

    async def on_submit(self, interaction: discord.Interaction):
        user_id = str(self.buyer_id)
        balances = load_balances()
        solde = balances.get(user_id, 0)

        market = load_market()
        try:
            offer_id = int(self.offer_id.value)
        except ValueError:
            return await interaction.response.send_message("❌ ID invalide.", ephemeral=True)

        offer = next((m for m in market if m["id"] == offer_id), None)
        if not offer:
            return await interaction.response.send_message("❌ Offre introuvable.", ephemeral=True)

        if offer["vendeur_id"] == user_id:
            return await interaction.response.send_message("❌ Tu ne peux pas acheter ton propre objet.", ephemeral=True)

        if solde < offer["prix"]:
            return await interaction.response.send_message("❌ Tu n'as pas assez d'argent pour cet achat.", ephemeral=True)

        taxe = round(offer["prix"] * 0.05)
        prix_net = offer["prix"] - taxe

        # Paiement
        balances[user_id] = solde - offer["prix"]

        vendeur_id = offer.get("vendeur_id")
        if vendeur_id:
            solde_vendeur = balances.get(vendeur_id, 0)
            balances[vendeur_id] = solde_vendeur + prix_net

        save_balances(balances)

        # Ajout inventaire acheteur
        inventaires = load_inventory()
        inventaires.setdefault(user_id, []).append(offer["objet"])
        save_inventory(inventaires)

        # Retrait du marché
        market = [m for m in market if m["id"] != offer_id]
        save_market(market)

        await interaction.response.send_message(
            f"💸 <@{self.buyer_id}> a acheté **{offer['objet']}** pour {format_money(offer['prix'])} € "
            f"(taxe 5% = {taxe} €). Le vendeur {offer['vendeur']} reçoit {prix_net} €."
        )



# --- Modal pour définir le prix ---
class SellModal(discord.ui.Modal, title="💰 Mettre en vente un objet"):
    price = discord.ui.TextInput(
        label="Prix de vente (€)",
        placeholder="Exemple : 100",
        required=True
    )

    def __init__(self, buyer_id: int, item: str):
        super().__init__()
        self.buyer_id = buyer_id
        self.item = item

    async def on_submit(self, interaction: discord.Interaction):
        if interaction.user.id != self.buyer_id:
            return await interaction.response.send_message("❌ Ce n'est pas ton inventaire.", ephemeral=True)

        try:
            price = int(self.price.value)
        except ValueError:
            return await interaction.response.send_message("❌ Prix invalide.", ephemeral=True)

        if price <= 0:
            return await interaction.response.send_message("❌ Le prix doit être supérieur à 0 €.", ephemeral=True)

        user_id = str(self.buyer_id)
        inventaires = load_inventory()
        items = inventaires.get(user_id, [])

        if self.item not in items:
            return await interaction.response.send_message("❌ Objet introuvable dans ton inventaire.", ephemeral=True)

        # Limite de ventes
        market = load_market()
        ventes_user = [m for m in market if m["vendeur_id"] == user_id]
        if len(ventes_user) >= 5:
            return await interaction.response.send_message(
                "❌ Tu as déjà 5 objets en vente. Retire une annonce avant d’en ajouter une autre.", ephemeral=True
            )

        # Retirer l'objet de l'inventaire
        items.remove(self.item)
        inventaires[user_id] = items
        save_inventory(inventaires)

        # Ajouter sur le marché
        new_id = max([m["id"] for m in market], default=0) + 1
        market.append({
            "id": new_id,
            "vendeur": interaction.user.display_name,
            "vendeur_id": user_id,
            "objet": self.item,
            "prix": price
        })
        save_market(market)

        # ✅ Confirmation à l’utilisateur (privée)
        await interaction.response.send_message(
            f"✅ {interaction.user.mention} a mis en vente **{self.item}** pour {format_money(price)} € (ID {new_id}).",
            ephemeral=True
        )

        # 📢 Annonce publique dans le salon spécial
        channel_id = 1409832493447778314  # 👉 remplace par l'ID du salon de ventes
        channel = interaction.client.get_channel(channel_id)
        if channel:
            await channel.send(
                f"📢 **NOUVELLE VENTE !**\n"
                f"🧑 Vendeur : {interaction.user.mention}\n"
                f"📦 Objet : **{self.item}**\n"
                f"💰 Prix : {format_money(price)} €\n"
                f"🆔 ID : `{new_id}`"
            )



# --- Sélecteur avec pagination ---
class InventorySelect(discord.ui.Select):
    def __init__(self, items, buyer_id, page=0, items_per_page=25):
        self.items = items
        self.buyer_id = buyer_id
        self.page = page
        self.items_per_page = items_per_page

        start = page * items_per_page
        end = start + items_per_page
        page_items = items[start:end]

        options = [
            discord.SelectOption(
                label=item,
                value=f"{idx}-{item}"  # Valeur unique
            )
            for idx, item in enumerate(page_items, start=start)
        ]

        super().__init__(
            placeholder=f"🛒 Page {page+1} | Choisis un objet à mettre en vente",
            options=options,
            min_values=1,
            max_values=1
        )

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.buyer_id:
            return await interaction.response.send_message("❌ Ce n'est pas ton inventaire.", ephemeral=True)

        idx = int(self.values[0].split("-")[0])
        item_to_sell = self.items[idx]
        await interaction.response.send_modal(SellModal(interaction.user.id, item_to_sell))


# --- Vue avec navigation ---
class InventoryView(discord.ui.View):
    def __init__(self, items, buyer_id, page=0, items_per_page=25):
        super().__init__(timeout=60)
        self.items = items
        self.buyer_id = buyer_id
        self.page = page
        self.items_per_page = items_per_page

        self.select = InventorySelect(items, buyer_id, page, items_per_page)
        self.add_item(self.select)

        # Boutons navigation
        self.add_item(PrevInvButton())
        self.add_item(NextInvButton())

    async def update_page(self, interaction, page):
        self.page = page
        self.remove_item(self.select)
        self.select = InventorySelect(self.items, self.buyer_id, page, self.items_per_page)
        self.add_item(self.select)
        await interaction.response.edit_message(content=f"🛒 Inventaire - page {page+1}", view=self)


class PrevInvButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="⬅️", style=discord.ButtonStyle.secondary)

    async def callback(self, interaction: discord.Interaction):
        view: InventoryView = self.view
        if view.page > 0:
            await view.update_page(interaction, view.page - 1)


class NextInvButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="➡️", style=discord.ButtonStyle.secondary)

    async def callback(self, interaction: discord.Interaction):
        view: InventoryView = self.view
        max_page = (len(view.items) - 1) // view.items_per_page
        if view.page < max_page:
            await view.update_page(interaction, view.page + 1)


# --- Commande vendre ---
@bot.command()
async def vendre(ctx):
    user_id = str(ctx.author.id)
    inventaires = load_inventory()
    items = inventaires.get(user_id, [])

    if not items:
        return await ctx.send("❌ Ton inventaire est vide.")

    view = InventoryView(items, ctx.author.id)
    await ctx.send("🛒 Sélectionne l'objet que tu veux mettre en vente :", view=view)



# --- TrashSelect ---
class TrashSelect(Select):
    def __init__(self, items, user_id, page=0):
        self.user_id = user_id
        self.items_list = items
        self.page = page

        # On coupe la liste en blocs de 25 max
        start = page * 25
        end = start + 25
        page_items = items[start:end]

        options = [
            discord.SelectOption(label=item, value=str(start + i), description=f"Jeter {item}") 
            for i, item in enumerate(page_items)
        ]

        super().__init__(placeholder=f"Page {page+1}", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Ce n'est pas ton inventaire !", ephemeral=True)
            return

        inventaires = load_inventory()
        user_items = inventaires.get(str(self.user_id), [])

        selected_index = int(self.values[0])
        selected_item = self.items_list[selected_index]

        if selected_item in user_items:
            user_items.remove(selected_item)
            inventaires[str(self.user_id)] = user_items
            save_inventory(inventaires)

            if user_items:
                new_view = TrashView(user_items, self.user_id, self.page)
                await interaction.response.edit_message(
                    content=f"🗑️ Tu as jeté **{selected_item}**. Choisis un autre objet à jeter :",
                    view=new_view
                )
            else:
                await interaction.response.edit_message(
                    content=f"🗑️ Tu as jeté **{selected_item}**. Ton inventaire est maintenant vide.",
                    view=None
                )

# --- TrashView ---
class TrashView(View):
    def __init__(self, items, user_id, page=0):
        super().__init__(timeout=None)
        self.user_id = user_id
        self.items = items
        self.page = page

        self.add_item(TrashSelect(items, user_id, page))

        # Boutons pour naviguer entre les pages
        if len(items) > 25:
            if page > 0:
                self.add_item(PreviousPageButton())
            if (page + 1) * 25 < len(items):
                self.add_item(NextPageButton())

# --- Boutons de pagination ---
class PreviousPageButton(Button):
    def __init__(self):
        super().__init__(label="⬅️ Précédent", style=discord.ButtonStyle.secondary)

    async def callback(self, interaction: discord.Interaction):
        view: TrashView = self.view
        new_page = view.page - 1
        await interaction.response.edit_message(
            view=TrashView(view.items, view.user_id, new_page)
        )

class NextPageButton(Button):
    def __init__(self):
        super().__init__(label="➡️ Suivant", style=discord.ButtonStyle.secondary)

    async def callback(self, interaction: discord.Interaction):
        view: TrashView = self.view
        new_page = view.page + 1
        await interaction.response.edit_message(
            view=TrashView(view.items, view.user_id, new_page)
        )

# --- Commande jeter ---
@bot.command()
async def jeter(ctx):
    user_id = ctx.author.id
    inventaires = load_inventory()
    items = inventaires.get(str(user_id), [])

    if not items:
        return await ctx.send("❌ Ton inventaire est vide.")

    view = TrashView(items, user_id, page=0)
    await ctx.send("🗑️ Sélectionne l'objet que tu veux jeter :", view=view)



def generate_market_embed(offers, page=0, items_per_page=5):
    start = page * items_per_page
    end = start + items_per_page
    chunk = offers[start:end]

    embed = discord.Embed(
        title="🏪 Marché des joueurs",
        description=f"Page {page + 1}/{(len(offers)-1)//items_per_page + 1}",
        color=discord.Color.blurple()
    )

    if not chunk:
        embed.description = "📭 Aucune offre sur cette page."
        return embed

    for offer in chunk:
        embed.add_field(
            name=f"{offer['objet']}",
            value=f"👤 Vendeur : **{offer['vendeur']}**\n💰 Prix : **{format_money(offer['prix'])} €**",
            inline=False
        )

    embed.set_footer(text=f"{len(offers)} offres au total")
    return embed



class MarketSelect(discord.ui.Select):
    def __init__(self, offers, page=0, items_per_page=5):
        self.offers = offers
        self.page = page
        self.items_per_page = items_per_page
        options = self._get_options()
        super().__init__(placeholder="🛒 Choisis un objet à acheter", options=options)

    def _get_options(self):
        start = self.page * self.items_per_page
        end = start + self.items_per_page
        chunk = self.offers[start:end]

        return [
            discord.SelectOption(
                label=f"{offer['objet']} - {format_money(offer['prix'])}€",
                description=f"Vendeur : {offer['vendeur']}",
                value=str(offer["id"])
            )
            for offer in chunk
        ]

    async def update_options(self):
        self.options = self._get_options()

    async def callback(self, interaction: discord.Interaction):
        buyer_id = interaction.user.id
        selected_id = int(self.values[0])

        # ⚡ Ici on appelle process_purchase pour exécuter l'achat
        result = process_purchase(buyer_id, selected_id)

        # Message de retour (succès ou erreur)
        await interaction.response.send_message(result, ephemeral=True)

        # Recharge la vue pour que l’offre disparaisse si elle a été achetée
        offers = load_market()
        view = MarketView(offers, self.page, self.items_per_page)
        embed = generate_market_embed(offers, self.page, self.items_per_page)
        await interaction.message.edit(embed=embed, view=view)



class MarketView(discord.ui.View):
    def __init__(self, offers, page=0, items_per_page=5):
        super().__init__(timeout=None)
        self.offers = offers
        self.page = page
        self.items_per_page = items_per_page

        # Création du select pour la page initiale
        self.select = MarketSelect(offers, page, items_per_page)
        self.add_item(self.select)

        # Boutons navigation
        self.add_item(PrevButton())
        self.add_item(NextButton())

    async def update_page(self, interaction: discord.Interaction, page: int):
        self.page = page

        # ⚡ Recrée un nouveau Select adapté à la page
        self.remove_item(self.select)
        self.select = MarketSelect(self.offers, page, self.items_per_page)
        self.add_item(self.select)

        # Met à jour l’embed
        embed = generate_market_embed(self.offers, page, self.items_per_page)
        await interaction.response.edit_message(embed=embed, view=self)




class PrevButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="◀️", style=discord.ButtonStyle.primary)

    async def callback(self, interaction: discord.Interaction):
        view: MarketView = self.view
        if view.page > 0:
            await view.update_page(interaction, view.page - 1)


class NextButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="▶️", style=discord.ButtonStyle.primary)

    async def callback(self, interaction: discord.Interaction):
        view: MarketView = self.view
        max_page = (len(view.offers) - 1) // view.items_per_page
        if view.page < max_page:
            await view.update_page(interaction, view.page + 1)


def process_purchase(buyer_id, offer_id):
    market = load_market()
    balances = load_balances()

    # Trouver l'offre correspondante
    offer = next((o for o in market if o["id"] == offer_id), None)
    if not offer:
        return "❌ Offre introuvable."

    vendeur_id = str(offer["vendeur_id"])
    objet = offer["objet"]
    prix = offer["prix"]

    # Vérif solde acheteur
    buyer_id = str(buyer_id)
    if balances.get(buyer_id, 0) < prix:
        return "❌ Tu n’as pas assez d’argent."

    # Anti auto-achat (se racheter soi-même)
    if buyer_id == vendeur_id:
        return "❌ Tu ne peux pas racheter ton propre objet."

    # Débit / crédit
    balances[buyer_id] = balances.get(buyer_id, 0) - prix
    balances[vendeur_id] = balances.get(vendeur_id, 0) + prix

    # Ajouter objet à l'inventaire acheteur
    inventories = load_inventory()
    inventories.setdefault(buyer_id, []).append(objet)
    save_inventory(inventories)

    # Retirer l'offre du marché
    market = [o for o in market if o["id"] != offer_id]
    save_market(market)

    # Sauvegarder les soldes
    save_balances(balances)

    return f"✅ Tu as acheté **{objet}** pour {format_money(prix)}€."


@bot.command()
async def market(ctx):
    offers = load_market()
    if not offers:
        await ctx.send("📭 Le marché est vide.")
        return

    # Génère l'embed de la première page du marché
    embed = generate_market_embed(offers, 0, 5)

    # Passe seulement les offres à MarketView (buyer_id est géré via interaction.user.id)
    view = MarketView(offers)  # <-- ici

    await ctx.send(embed=embed, view=view)





@bot.command()
async def buy(ctx, *, item_name: str):
    item_name = item_name.strip().lower()
    found_item = None

    # Recherche insensible à la casse
    for name in shop_items:
        if name.lower() == item_name:
            found_item = name
            break

    if not found_item:
        return await ctx.send("❌ Cet objet n'existe pas dans le shop.")

    price = shop_items[found_item]
    user_id = str(ctx.author.id)
    balances = load_balances()
    solde = balances.get(user_id, 0)

    if solde < price:
        return await ctx.send(
            f"❌ Tu n'as pas assez d'argent pour acheter {found_item}. Solde actuel : {format_money(solde)} €"
        )

    # Déduire le prix
    balances[user_id] = solde - price
    save_balances(balances)

    # Ajouter dans l'inventaire
    inventaires = load_inventory()
    if user_id not in inventaires:
        inventaires[user_id] = []
    inventaires[user_id].append(found_item)
    save_inventory(inventaires)

    await ctx.send(
        f"✅ {ctx.author.mention} a acheté **{found_item}** pour {format_money(price)} €."
    )

from discord.ext import commands

@bot.command()
@commands.has_permissions(administrator=True)  # seulement les admins
async def cancel_offer(ctx, offer_id: int):
    """Supprime une offre du marché et rembourse le vendeur (ADMIN)."""
    market = load_market()
    balances = load_balances()
    inventories = load_inventory()

    # Cherche l'offre
    offer = next((o for o in market if o["id"] == offer_id), None)
    if not offer:
        return await ctx.send("❌ Offre introuvable.")

    vendeur_id = str(offer["vendeur_id"])
    objet = offer["objet"]
    prix = offer["prix"]

    # 🔄 Remet l'objet dans l'inventaire du vendeur
    inventories.setdefault(vendeur_id, []).append(objet)
    save_inventory(inventories)

    # 🔄 Rembourse le vendeur
    balances[vendeur_id] = balances.get(vendeur_id, 0) + prix
    save_balances(balances)

    # ❌ Supprime l'offre du marché
    market = [o for o in market if o["id"] != offer_id]
    save_market(market)

    await ctx.send(
        f"✅ Offre **{offer_id}** annulée.\n"
        f"L'objet **{objet}** a été rendu au vendeur <@{vendeur_id}> "
        f"et {format_money(prix)} € lui ont été remboursés."
    )


@bot.command()
async def inventory(ctx, member: discord.Member = None):
    member = member or ctx.author
    user_id = str(member.id)
    inventaires = load_inventory()
    items = inventaires.get(user_id, [])

    if not items:
        return await ctx.send(f"📦 {member.mention} n'a rien dans son inventaire.")

    item_counts = list(Counter(items).items())  # [(item, qty), ...]
    per_page = 10
    total_pages = ceil(len(item_counts) / per_page)

    def create_page(page_index):
        embed = discord.Embed(
            title=f"📦 Inventaire de {member.display_name} — Page {page_index+1}/{total_pages}",
            color=discord.Color.gold()
        )
        start = page_index * per_page
        end = start + per_page
        for item, count in item_counts[start:end]:
            embed.add_field(name=item, value=f"× {count}", inline=False)
        embed.set_footer(text=f"Demandé par {ctx.author.display_name}", icon_url=ctx.author.display_avatar.url)
        return embed

    current_page = 0

    class InventoryView(discord.ui.View):
        def __init__(self):
            super().__init__(timeout=120)
            self.update_buttons()

        def update_buttons(self):
            for child in self.children:
                if isinstance(child, discord.ui.Button):
                    if child.custom_id == "prev":
                        child.disabled = current_page == 0
                    elif child.custom_id == "next":
                        child.disabled = current_page == total_pages - 1

        async def interaction_check(self, interaction: discord.Interaction) -> bool:
            if interaction.user != ctx.author:
                await interaction.response.send_message("❌ Ce n'est pas ton inventaire.", ephemeral=True)
                return False
            return True

        @discord.ui.button(label="◀️", style=discord.ButtonStyle.secondary, custom_id="prev")
        async def prev_button(self, interaction: discord.Interaction, button: discord.ui.Button):
            nonlocal current_page
            if current_page > 0:
                current_page -= 1
                self.update_buttons()
                await interaction.response.edit_message(embed=create_page(current_page), view=self)

        @discord.ui.button(label="▶️", style=discord.ButtonStyle.secondary, custom_id="next")
        async def next_button(self, interaction: discord.Interaction, button: discord.ui.Button):
            nonlocal current_page
            if current_page < total_pages - 1:
                current_page += 1
                self.update_buttons()
                await interaction.response.edit_message(embed=create_page(current_page), view=self)

        async def on_timeout(self):
            # Désactive les boutons après expiration
            for child in self.children:
                if isinstance(child, discord.ui.Button):
                    child.disabled = True
            # Édite le dernier message pour refléter les boutons désactivés
            async for message in ctx.channel.history(limit=50):
                if message.author == bot.user and message.embeds:
                    await message.edit(view=self)
                    break

    view = InventoryView()
    await ctx.send(embed=create_page(current_page), view=view)


MATCHS_FILE = "matchs.json"

# --- Fonctions utilitaires ---
def load_json(filename):
    try:
        with open(filename, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_json(filename, data):
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)


# --- Commande pour créer un match ---
@bot.command()
@commands.has_permissions(administrator=True)
async def match(ctx, team1, team2, cote1: float, coteN: float, cote2: float, date_heure: str):
    """
    Ajoute un match avec date et heure. Si seulement HH:MM est fourni, date = aujourd'hui.
    """
    matchs = load_json(MATCHS_FILE)
    match_id = f"{team1.lower()}-{team2.lower()}"

    # Détection format
    try:
        # Si format YYYY-MM-DD HH:MM
        dt = datetime.strptime(date_heure, "%Y-%m-%d %H:%M")
    except ValueError:
        try:
            # Si seulement HH:MM, on ajoute la date d'aujourd'hui
            dt = datetime.strptime(datetime.today().strftime("%Y-%m-%d") + " " + date_heure, "%Y-%m-%d %H:%M")
        except ValueError:
            await ctx.send("❌ Format invalide. Utilisez YYYY-MM-DD HH:MM ou juste HH:MM (ex: 20:45).")
            return

    matchs[match_id] = {
        "team1": team1,
        "team2": team2,
        "cote1": cote1,
        "coteN": coteN,
        "cote2": cote2,
        "date_heure": dt.strftime("%Y-%m-%d %H:%M"),
        "bets": {}
    }
    save_json(MATCHS_FILE, matchs)

    # Affichage
    if dt.date() == datetime.today().date():
        date_str = f"Aujourd'hui à {dt.strftime('%H:%M')}"
    else:
        date_str = dt.strftime("%d/%m/%Y %H:%M")

    await ctx.send(
        f"📢 Match ajouté : **{team1} vs {team2}**\n"
        f"🕒 Paris jusqu'au **{date_str}**\n"
        f"1️⃣ {team1} : {cote1}\n"
        f"🔄 Nul : {coteN}\n"
        f"2️⃣ {team2} : {cote2}"
    )



# --- Modal pour saisir le montant ---
class BetModal(Modal):
    def __init__(self, match_id, choix):
        super().__init__(title=f"Pari sur {choix}")
        self.match_id = match_id
        self.choix = choix

        self.montant = TextInput(
            label="Montant à miser 💰",
            placeholder="Ex: 50000",
            required=True
        )
        self.add_item(self.montant)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            montant_str = self.montant.value.replace(" ", "").replace(",", "")
            montant = int(montant_str)
        except ValueError:
            await interaction.response.send_message("⚠️ Le montant doit être un nombre valide.", ephemeral=True)
            return

        await bet(interaction, self.match_id, self.choix, montant)



# --- Vue avec 3 boutons ---
class BetView(View):
    def __init__(self, match_id):
        super().__init__(timeout=None)
        self.match_id = match_id

    @button(label="1️⃣", style=discord.ButtonStyle.green)
    async def bet_team1(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(BetModal(self.match_id, "1"))

    @button(label="🔄 N", style=discord.ButtonStyle.grey)
    async def bet_draw(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(BetModal(self.match_id, "N"))

    @button(label="2️⃣", style=discord.ButtonStyle.red)
    async def bet_team2(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(BetModal(self.match_id, "2"))


def parse_montant(val: str) -> int:
    """Convertit une entrée texte en int (ex: '20 000', '2M', '1.5k')."""
    val = val.replace(" ", "").replace(",", "").lower()
    if val.endswith("k"):
        return int(float(val[:-1]) * 1000)
    if val.endswith("m"):
        return int(float(val[:-1]) * 1_000_000)
    return int(val)



# --- Fonction bet adaptée (ctx OU interaction) ---
async def bet(ctx_or_inter, match_id, choix, montant_input):
    balances = load_json(BALANCES_FILE)
    matchs = load_json(MATCHS_FILE)

    # Identifier l'utilisateur + fonction d'envoi
    if isinstance(ctx_or_inter, discord.Interaction):
        user_id = str(ctx_or_inter.user.id)
        async def send_func(msg):
            await ctx_or_inter.response.send_message(msg, ephemeral=True)
    else:
        user_id = str(ctx_or_inter.author.id)
        async def send_func(msg):
            await ctx_or_inter.send(msg)

    # Vérification du match
    if match_id not in matchs:
        return await send_func("❌ Match introuvable.")

    match_data = matchs[match_id]

    # Vérification date + heure limite
    try:
        dt_limite = datetime.strptime(match_data["date_heure"], "%Y-%m-%d %H:%M")
    except Exception:
        return await send_func("❌ Date/heure du match invalide.")

    now = datetime.now()
    if now > dt_limite:
        return await send_func("⏰ Les paris sont fermés pour ce match.")

    # Parse du montant (gère les formats avec espaces ou séparateurs)
    try:
        montant = parse_montant(str(montant_input))
    except ValueError:
        return await send_func("❌ Montant invalide.")

    # Vérifications montants
    if montant > 2_000_000:
        return await send_func("💸 Refusé, 2M max.")
    if montant < 10_000:
        return await send_func("💸 Refusé, 10k min.")

    # Vérif solde
    if user_id not in balances or balances[user_id] < montant:
        return await send_func("💸 Solde insuffisant.")

    # Vérif si déjà parié
    if user_id in match_data["bets"]:
        return await send_func("❌ Tu as déjà parié sur ce match !")

    # Déduire et enregistrer
    balances[user_id] -= montant
    match_data["bets"][user_id] = {"choix": choix.upper(), "montant": montant}

    save_json(BALANCES_FILE, balances)
    save_json(MATCHS_FILE, matchs)

    return await send_func(
        f"✅ Pari placé sur **{choix.upper()}** ({match_id}) pour {montant:,} 💰.\n"
        f"💳 Nouveau solde : {balances[user_id]:,} 💰"
    )



@bot.command()
@commands.has_permissions(administrator=True)
async def viewinv(ctx, member: discord.Member):
    inventaires = load_inventory()
    user_id = str(member.id)

    if user_id not in inventaires or len(inventaires[user_id]) == 0:
        await ctx.send(f"❌ {member.display_name} n'a pas d'inventaire.")
        return

    items = inventaires[user_id]
    description = "\n".join([f"- {item}" for item in items])

    embed = discord.Embed(
        title=f"Inventaire de {member.display_name}",
        description=description,
        color=discord.Color.blue()
    )
    embed.set_footer(text=f"Demandé par {ctx.author.display_name}")

    await ctx.send(embed=embed)

# =============================
# Gestion des erreurs
# =============================
@viewinv.error
async def viewinv_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ Tu n'as pas la permission d'utiliser cette commande.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("❌ Utilisation: `!viewinv @user`")
        
        
@bot.command()
@commands.has_permissions(administrator=True)
async def addinv(ctx, member: discord.Member, *, item: str):
    """Ajoute un objet à l'inventaire d'un membre."""
    inventory = load_inventory()
    user_id = str(member.id)
    if user_id not in inventory:
        inventory[user_id] = []

    inventory[user_id].append(item)
    save_inventory(inventory)
    await ctx.send(f"✅ L'objet **{item}** a été ajouté à l'inventaire de {member.display_name}.")


# --- Commande pour voir les matchs avec boutons ---
@bot.command()
async def matchs(ctx):
    matchs_data = load_json(MATCHS_FILE)
    
    if not matchs_data:
        return await ctx.send("❌ Aucun match en cours.")

    aujourdhui = datetime.today().date()  # juste la date

    for match_id, data in matchs_data.items():
        try:
            dt = datetime.strptime(data["date_heure"], "%Y-%m-%d %H:%M")
        except Exception:
            await ctx.send(f"❌ Format date/heure invalide pour le match {match_id}.")
            continue

        # Si la date du match est aujourd'hui
        if dt.date() == aujourdhui:
            date_str = f"Aujourd'hui à {dt.strftime('%H:%M')}"
        else:
            date_str = dt.strftime("%d/%m/%Y %H:%M")

        embed = discord.Embed(
            title=f"⚽ {data['team1']} vs {data['team2']}",
            description=f"ID : `{match_id}`\n⏰ Paris jusqu'à {date_str}",
            color=discord.Color.blue()
        )
        embed.add_field(
            name="Cotes",
            value=f"1️⃣ {data['team1']} : {data['cote1']}\n🔄 Nul : {data['coteN']}\n2️⃣ {data['team2']} : {data['cote2']}",
            inline=False
        )
        total_bets = sum(b['montant'] for b in data["bets"].values())
        embed.set_footer(text=f"Total des mises : {total_bets} 💰")
        await ctx.send(embed=embed, view=BetView(match_id))




# --- Commande pour terminer un match ---
@bot.command()
@commands.has_permissions(administrator=True)
async def endmatch(ctx, match_id, resultat):
    balances = load_balances()
    matchs = load_json(MATCHS_FILE)

    if match_id not in matchs:
        await ctx.send("❌ Match introuvable.")
        return

    match_data = matchs[match_id]

    # Vérif résultat
    if resultat == "1":
        cote = match_data["cote1"]
    elif resultat.upper() == "N":
        cote = match_data["coteN"]
    elif resultat == "2":
        cote = match_data["cote2"]
    else:
        await ctx.send("❌ Résultat invalide (1, N ou 2).")
        return

    if not match_data["bets"]:  # aucun pari
        del matchs[match_id]
        save_json(MATCHS_FILE, matchs)
        await ctx.send(f"📊 Match terminé ({resultat})\n⚠️ Personne n'a parié sur ce match.")
        return

    gains_total = []
    for user_id, bet in match_data["bets"].items():
        if bet["choix"] == resultat.upper():
            gain = int(bet["montant"] * cote)
            balances[user_id] = balances.get(user_id, 0) + gain
            gains_total.append((user_id, gain))

    # Suppression du match terminé
    del matchs[match_id]
    save_balances(balances)
    save_json(MATCHS_FILE, matchs)

    # Message de résultats
    if gains_total:
        msg = "\n".join([f"<@{uid}> gagne {format_money(g)} 💰" for uid, g in gains_total])
    else:
        msg = "😢 Personne n'a gagné."
    await ctx.send(f"📊 Match terminé ({resultat})\n{msg}")




@bot.command()
async def topriches(ctx, n: int = 10):
    balances = load_balances()
    top = sorted(balances.items(), key=lambda x: x[1], reverse=True)[:n]

    if not top:
        return await ctx.send("💸 Aucun utilisateur n'a d'argent.")

    embed = discord.Embed(title=f"🏆 Top {n} des plus riches",
                          color=discord.Color.gold())

    medals = ["🥇", "🥈", "🥉"]

    for i, (user_id, balance) in enumerate(top, start=1):
        try:
            user = await bot.fetch_user(int(user_id))
            if user:
                username = user.display_name
                mention = user.mention
            else:
                username = f"Utilisateur inconnu ({user_id})"
                mention = ""

            formatted_balance = format_money(balance)
            medal = medals[i - 1] if i <= len(medals) else f"#{i}"

            embed.add_field(name=f"{medal} {username}",
                            value=f"💰 {formatted_balance} € — {mention}",
                            inline=False)

        except Exception as e:
            print(f"Erreur en récupérant l'utilisateur {user_id} : {e}")

    await ctx.send(embed=embed)


@bot.command()
async def objectif(ctx):
    objectifs = [
        "🎯 Marquer 3 buts en 2 matchs", "🎯 Marquer 4 buts en 5 matchs",
        "🎯 Marquer 3 buts en 3 matchs", "🎯 Marquer 6 buts en 7 matchs",
        "🎯 Marquer un but spectaculaire !", "🎯 Marquer de la tête",
        "🎯 Marquer sur coup franc direct", "🎯 Marquer du pied faible",
        "🎯 Marquer dans les arrêts de jeu",
        "🎯 Marquer un doublé dans le prochain match", "🎯 Marquer sur penalty",
        "🎯 Marquer dans 3 matchs consécutifs",
        "🎯 Marquer un but contre un rival", "🎯 Marquer après un dribble",
        "🎯 Marquer après un une-deux",
        "📊 Faire 2 passes décisives cette semaine",
        "📊 Faire 4 passes décisives cette semaine",
        "📊 Faire 1 passe décisive de l’extérieur du pied",
        "📊 Faire une passe décisive à chaque match cette semaine",
        "📊 Être impliqué sur 3 buts en 2 matchs",
        "📊 Faire 2 avant-dernières passes décisives",
        "🧱 Ne pas encaisser de but pour le prochain match",
        "🧱 Réaliser 3 tacles propres en un match",
        "🧱 Gagner 10 duels défensifs en 2 matchs",
        "🧱 Ne pas commettre de faute pendant un match",
        "🧱 Bloquer 5 tirs en 3 matchs",
        "🧱 Être l’un des 3 meilleurs défenseurs du match selon les notes",
        "⚡ Courir plus de 10km dans le prochain match",
        "⚡ Réaliser 5 sprints à haute intensité",
        "⚡ Récupérer 8 ballons en un match",
        "⚡ Gagner tous tes duels aériens pendant un match",
        "⚡ Gagner plus de 80% de tes duels en 2 matchs",
        "💬 Répondre à 5 interviews RP",
        "💬 Créer une polémique en interview RP",
        "💬 Féliciter un coéquipier en RP",
        "💬 Rejeter une question de journaliste en RP",
        "💬 Faire une déclaration ambitieuse RP", "🧠 Améliore ta vitesse",
        "🧠 Améliore ta finition", "🧠 Améliore ta vision du jeu",
        "🧠 Améliore ton jeu de tête", "🧠 Améliore ton positionnement défensif",
        "🔥 Devenir homme du match dans le prochain match",
        "🔥 Obtenir la meilleure note de ton équipe",
        "🔥 Réaliser un match sans perdre un seul ballon",
        "🔥 Créer 5 occasions franches dans un match",
        "🔥 Être décisif dans les 10 dernières minutes",
        "🔥 Enchaîner 3 bonnes performances de suite",
        "👟 Réussir 5 dribbles dans un match",
        "👟 Réussir un grand pont + un crochet dans le même match",
        "👟 Eliminer 3 adversaires sur une même action",
        "👟 Provoquer un penalty",
        "👟 Faire un sombrero ou un geste technique RP",
        "🧤 Arrêter un penalty (si gardien)",
        "🧤 Réaliser 4 arrêts décisifs dans un match",
        "🧤 Garder 2 clean sheets d'affilée",
        "🧤 Être élu meilleur gardien de la journée",
        "🧤 Détourner un coup franc bien placé",
        "🧤 Gagner 100% de ses sorties aériennes", "🧠 Analyser un match RP",
        "🎓 Encadrer un jeune joueur RP",
        "📣 Motiver tes coéquipiers dans le vestiaire RP",
        "🔁 Participer à une rotation de poste RP",
        "🧾 Négocier une prolongation RP",
        "🎯 Être impliqué dans tous les buts de l’équipe sur 2 matchs",
        "🎯 Être passeur ET buteur dans le même match", "🔥 Réaliser un triplé",
        "📊 Être 1er aux stats individuelles (buts, passes, tacles…) cette semaine",
        "📣 Être élu capitaine pour un match (RP)",
        "📊 Réaliser 90% de passes réussies dans un match"
    ]

    objectif = random.choice(objectifs)
    await ctx.send(f"🎯 Ton objectif : **{objectif}**")


API_KEY = "c16a7d1c38314ad589bc5c96649389fa"

SYMBOLS = ["AAPL", "MSFT", "TSLA", "GOOGL", "AMZN", "NVDA", "BRK.A"]
PORTF_FILE = "portefeuille.json"


def get_quotes(symbols):
    url = "https://api.twelvedata.com/quote"
    quotes = []
    for symbol in symbols:
        params = {"symbol": symbol, "apikey": API_KEY}
        r = requests.get(url, params=params)
        data = r.json()
        print(f"[DEBUG] Réponse API pour {symbol}:", data)

        if all(k in data for k in ("name", "close", "percent_change")):
            quotes.append({
                "nom": data["name"],
                "symbole": symbol,
                "prix": float(data["close"]),
                "variation": float(data["percent_change"])
            })
        elif "message" in data:
            print(f"[ERREUR API {symbol}] {data['message']}")
    return quotes


def load_portefeuille():
    try:
        with open(PORTF_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def save_portefeuille(portefeuille):
    with open(PORTF_FILE, "w") as f:
        json.dump(portefeuille, f, indent=4)


def quotes_list_to_dict(quotes_list):
    return {q["symbole"]: q for q in quotes_list}



@bot.command()
async def portefeuille(ctx):
    portefeuille = load_portefeuille()
    user_id = str(ctx.author.id)
    if user_id not in portefeuille or not portefeuille[user_id]:
        await ctx.send("💼 Ton portefeuille est vide.")
        return

    symbols = list(portefeuille[user_id].keys())
    quotes_list = get_quotes(symbols)
    quotes = quotes_list_to_dict(quotes_list)

    total_investi = 0
    total_valeur = 0

    embed = Embed(
        title=f"📊 Portefeuille de {ctx.author.display_name}",
        color=0x1abc9c
    )

    for symbol, data in portefeuille[user_id].items():
        if symbol not in quotes:
            prix_actuel = 0
            variation = 0
            nom = symbol
        else:
            prix_actuel = quotes[symbol]["prix"]
            variation = quotes[symbol]["variation"]
            nom = quotes[symbol]["nom"]

        valeur_actuelle = data["actions"] * prix_actuel
        gain_perte = valeur_actuelle - data["investi"]
        pct_gain = (gain_perte / data["investi"] * 100) if data["investi"] > 0 else 0
        total_investi += data["investi"]
        total_valeur += valeur_actuelle

        emoji = "📈" if gain_perte > 0 else "📉" if gain_perte < 0 else "➖"

        embed.add_field(
            name=f"**{nom} ({symbol})**",
            value=(
                f"💵 Investi: **${data['investi']:.2f}**\n"
                f"📊 Actions: **{data['actions']:.4f}**\n"
                f"💰 Valeur: **${valeur_actuelle:.2f}** {emoji}\n"
                f"📈 Variation: **{variation:+.2f}%**\n"
                f"📉 Gain/Perte: **{gain_perte:+.2f}$ ({pct_gain:+.2f}%)**"
            ),
            inline=False
        )

    total_gain = total_valeur - total_investi
    embed.add_field(
        name="📌 Résumé",
        value=(
            f"💵 **Total investi :** ${total_investi:.2f}\n"
            f"💰 **Valeur actuelle :** ${total_valeur:.2f}\n"
            f"📉 **Gain/Perte total :** {total_gain:+.2f}$"
        ),
        inline=False
    )

    await ctx.send(embed=embed)



# --- Investir dans une action ---
@bot.command()
async def invest(ctx, symbol: str, montant: float):
    symbol = symbol.upper()
    if symbol not in SYMBOLS:
        await ctx.send(f"❌ Le symbole {symbol} n'est pas supporté.")
        return

    if montant < 1000 or montant > 10000000:  # Limites d’investissement
        await ctx.send("❌ Montant invalide : minimum 1 000$, maximum 10 000 000$.") 
        return

    if get_balance(str(ctx.author.id)) < montant:  # Vérifie le solde
        await ctx.send("💸 Solde insuffisant pour cet investissement.")
        return

    quotes_list = get_quotes([symbol])
    if not quotes_list:
        await ctx.send(f"❌ Données introuvables pour {symbol}.")
        return

    quotes = quotes_list_to_dict(quotes_list)
    prix = quotes[symbol]["prix"]
    quantite = montant / prix

    portefeuille = load_portefeuille()
    user_id = str(ctx.author.id)
    if user_id not in portefeuille:
        portefeuille[user_id] = {}

    # Mise à jour du portefeuille avec calcul du prix moyen
    if symbol in portefeuille[user_id]:
        total_actions = portefeuille[user_id][symbol]["actions"] + quantite
        total_investi = portefeuille[user_id][symbol]["investi"] + montant
        portefeuille[user_id][symbol]["investi"] = total_investi
        portefeuille[user_id][symbol]["actions"] = total_actions
    else:
        portefeuille[user_id][symbol] = {"investi": montant, "actions": quantite}

    save_portefeuille(portefeuille)
    change_balance(user_id, -montant)

    embed = Embed(
        title=f"✅ Investissement réussi dans {symbol}",
        description=(
            f"💵 Montant investi : ${montant:.2f}\n"
            f"📊 Actions achetées : {quantite:.4f}\n"
            f"💰 Prix moyen : ${portefeuille[user_id][symbol]['investi'] / portefeuille[user_id][symbol]['actions']:.2f}"
        ),
        color=0x1abc9c
    )
    await ctx.send(embed=embed)


# --- Vendre une action ---
@bot.command()
async def sell(ctx, symbol: str, amount: str = "all"):
    symbol = symbol.upper()
    portefeuille = load_portefeuille()
    inventory = load_inventory()
    user_id = str(ctx.author.id)

    if user_id not in portefeuille or symbol not in portefeuille[user_id]:
        await ctx.send(f"❌ Tu ne possèdes aucune action {symbol}.")
        return

    data = portefeuille[user_id][symbol]
    total_actions = data["actions"]

    # Calcul du nombre d’actions à vendre
    if amount.lower().endswith("%"):  # Vente en pourcentage
        pct = float(amount[:-1]) / 100
        quantite = total_actions * pct
    elif amount.lower() == "all":  # Vente totale
        quantite = total_actions
    else:  # Vente d’un nombre précis
        quantite = float(amount)
    if quantite <= 0 or quantite > total_actions:
        await ctx.send("❌ Quantité invalide à vendre.")
        return

    quotes_list = get_quotes([symbol])
    if not quotes_list:
        await ctx.send(f"❌ Données pour {symbol} indisponibles.")
        return

    quotes = quotes_list_to_dict(quotes_list)
    prix_actuel = quotes[symbol]["prix"]
    valeur_vente = quantite * prix_actuel
    taxe = valeur_vente * 0.05
    valeur_net = valeur_vente - taxe

    prix_unitaire_achat = data["investi"] / data["actions"]
    valeur_achat = quantite * prix_unitaire_achat
    benefice = valeur_net - valeur_achat

    bonus = get_bonus(user_id, inventory)
    bonus_gain = benefice * bonus if benefice > 0 else 0
    gain_total = round(valeur_net + bonus_gain)

    # Mise à jour du portefeuille
    data["actions"] -= quantite
    data["investi"] -= prix_unitaire_achat * quantite
    if data["actions"] <= 0:
        del portefeuille[user_id][symbol]

    save_portefeuille(portefeuille)
    change_balance(user_id, gain_total)

    # Embed pour résumé
    embed = Embed(
        title=f"💸 Vente de {symbol}",
        color=0x2ecc71 if benefice > 0 else 0xe74c3c
    )
    embed.add_field(name="Quantité vendue", value=f"{quantite:.4f}", inline=True)
    embed.add_field(name="Prix actuel", value=f"${prix_actuel:.2f}", inline=True)
    embed.add_field(name="Valeur vente", value=f"${valeur_vente:.2f}", inline=True)
    embed.add_field(name="Taxe (5%)", value=f"${taxe:.2f}", inline=True)
    embed.add_field(name="Bénéfice brut", value=f"${benefice:+.2f}", inline=True)
    embed.add_field(name="Bonus appliqué", value=f"${bonus_gain:.2f}", inline=True)
    embed.add_field(name="Gain net", value=f"${gain_total}", inline=False)

    await ctx.send(embed=embed)


BOURSE_LIMIT_FILE = "bourse_limits.json"
BOURSE_DAILY_LIMIT = 5


def load_bourse_limits():
    if not os.path.exists(BOURSE_LIMIT_FILE):
        return {}
    with open(BOURSE_LIMIT_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_bourse_limits(data):
    with open(BOURSE_LIMIT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)



@bot.command()
async def bourse(ctx):
    """Affiche les cours des actions populaires (limite de 10 utilisations par jour)"""
    user_id = str(ctx.author.id)
    today = datetime.now().strftime("%Y-%m-%d")
    limits = load_bourse_limits()

    # Initialiser les données utilisateur si nécessaire
    if user_id not in limits or limits[user_id]["date"] != today:
        limits[user_id] = {"date": today, "count": 0}

    if limits[user_id]["count"] >= BOURSE_DAILY_LIMIT:
        await ctx.send(
            "🚫 Tu as atteint la limite quotidienne de 10 utilisations de la commande `!bourse`. Réessaie demain."
        )
        return

    # Augmente le compteur
    limits[user_id]["count"] += 1
    save_bourse_limits(limits)

    # Récupération des données
    infos = get_quotes(SYMBOLS)
    if not infos:
        await ctx.send("❌ Impossible de récupérer les cours pour le moment.")
        return

    # Trie par variation décroissante
    infos.sort(key=lambda x: float(x["variation"]), reverse=True)

    embed = Embed(title="📊 Marché Boursier - Aperçu",
                  color=discord.Color.blue())

    for info in infos:
        variation = float(info["variation"])
        fleche = "🔼" if variation >= 0 else "🔽"
        couleur = "🟢" if variation >= 0 else "🔴"


        embed.add_field(
            name=f"{info['nom']} ({info['symbole']})",
            value=(
                f"{couleur} **{info['prix']:.2f} $** {fleche} {variation:+.2f}%"
            ),
            inline=False
        )

    embed.set_footer(text=f"💡 Limite quotidienne : {limits[user_id]['count']}/{BOURSE_DAILY_LIMIT}")
    await ctx.send(embed=embed)



@bot.command()
@commands.has_permissions(administrator=True)
async def event(ctx, *, description: str):
    """Annonce un événement spécial avec un style amélioré."""
    colors = [discord.Color.purple(), discord.Color.gold(), discord.Color.blue(), discord.Color.green()]
    embed = discord.Embed(
        title="📢 **Événement spécial !**",
        description=f"👉 {description}",
        color=random.choice(colors),
        timestamp=datetime.utcnow()
    )
    
    # Icône en haut à gauche
    embed.set_thumbnail(url="https://cdn-icons-png.flaticon.com/512/326/326031.png")

    # Footer avec l’auteur
    embed.set_footer(
        text=f"Annonce par {ctx.author.display_name}",
        icon_url=ctx.author.avatar.url if ctx.author.avatar else None
    )

    await ctx.send(embed=embed)

    # Suppression du message de commande
    try:
        await ctx.message.delete()
    except discord.Forbidden:
        print("Le bot n’a pas la permission de supprimer ce message.")
    except discord.HTTPException as e:
        print(f"Erreur lors de la suppression du message : {e}")



@bot.command()
@commands.has_permissions(administrator=True)
async def reset_solde(ctx, member: discord.Member):
    user_id = str(member.id)
    balances[user_id] = 0
    save_balances(balances)
    await ctx.send(f"Le solde de {member.mention} a été réinitialisé à 0 €.")


@bot.command()
@commands.has_permissions(administrator=True)
async def supprimer_joueurs(ctx, member: discord.Member):
    user_id = str(member.id)
    if user_id in owned_players:
        del owned_players[user_id]
        save_owned_players(owned_players)
        await ctx.send(
            f"Tous les joueurs de {member.mention} ont été supprimés.")
    else:
        await ctx.send(f"{member.mention} ne possède aucun joueur.")


@bot.command()
@commands.has_permissions(administrator=True)
async def liste_ventes_admin(ctx):
    if not players_for_sale:
        await ctx.send("Aucun joueur n’est en vente.")
        return

    desc = ""
    for p in players_for_sale:
        desc += f"**{p['nom']}** - {p['valeur']} € - Vendeur: {p['vendeur_nom']}\n"

    embed = discord.Embed(title="Joueurs en vente (admin)",
                          description=desc,
                          color=discord.Color.red())
    await ctx.send(embed=embed)


@bot.command()
@commands.has_permissions(administrator=True)
async def retirer_vente(ctx, nom: str):
    global players_for_sale
    initial_len = len(players_for_sale)
    players_for_sale = [
        p for p in players_for_sale if p['nom'].lower() != nom.lower()
    ]
    save_players_for_sale(players_for_sale)

    if len(players_for_sale) < initial_len:
        await ctx.send(f"Le joueur **{nom}** a été retiré de la vente.")
    else:
        await ctx.send(f"Aucun joueur nommé **{nom}** n’a été trouvé.")


@bot.command()
async def set_solde(ctx, member: discord.Member, montant: int):
    # Autoriser uniquement certains IDs
    allowed_ids = [1397942510407516170, 511579819960565773]
    if ctx.author.id not in allowed_ids:
        await ctx.send("🚫 Vous n'êtes pas autorisé à utiliser cette commande.")
        return

    user_id = str(member.id)
    auteur = ctx.author.display_name
    balances[user_id] = montant
    save_balances(balances)
    print(f"Le solde de {member.mention} est maintenant de {montant} €.")
    print("auteur :", auteur)
    await ctx.send(
        f"Le solde de {member.mention} est maintenant de {montant} €.")


@bot.command()
@commands.has_permissions(administrator=True)
async def clear_ventes(ctx):
    players_for_sale.clear()
    save_players_for_sale(players_for_sale)
    await ctx.send("Tous les joueurs en vente ont été supprimés.")


@bot.command()
async def moneygive(ctx, montant: int):
    # Liste des IDs autorisés
    allowed_ids = [1397942510407516170, 511579819960565773]
    if ctx.author.id not in allowed_ids:
        await ctx.send("🚫 Vous n'êtes pas autorisé à utiliser cette commande.")
        return

    for member in ctx.guild.members:
        if not member.bot:
            user_id = str(member.id)
            balances[user_id] = balances.get(user_id, 0) + montant

    save_balances(balances)
    await ctx.send(f"💸 Tous les membres ont reçu {montant} €.")


@bot.command()
async def clearall(ctx):
    # IDs autorisés
    allowed_ids = [1397942510407516170, 511579819960565773]
    if ctx.author.id not in allowed_ids:
        await ctx.send("🚫 Vous n'êtes pas autorisé à utiliser cette commande.")
        return

    confirmation_msg = await ctx.send(
        "⚠️ Cette action va supprimer **toutes les données** (soldes, joueurs en vente, joueurs possédés).\n"
        "Réagis avec ✅ pour confirmer ou ❌ pour annuler.")
    await confirmation_msg.add_reaction("✅")
    await confirmation_msg.add_reaction("❌")

    def check(reaction, user):
        return user == ctx.author and str(reaction.emoji) in [
            "✅", "❌"
        ] and reaction.message.id == confirmation_msg.id

    try:
        reaction, user = await bot.wait_for("reaction_add",
                                            timeout=30.0,
                                            check=check)
    except asyncio.TimeoutError:
        await ctx.send("⏰ Temps écoulé. Suppression annulée.")
        return

    if str(reaction.emoji) == "✅":
        global balances, players_for_sale, owned_players

        balances = {}
        players_for_sale = []
        owned_players = {}

        save_balances(balances)
        save_players_for_sale(players_for_sale)
        save_owned_players(owned_players)

        await ctx.send("✅ Toutes les données ont été supprimées !")
    else:
        await ctx.send("❌ Suppression annulée.")


@clearall.error
async def clearall_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send(
            "❌ Tu dois être administrateur pour utiliser cette commande.")

    # Filtrer les membres avec le rôle Club (humains uniquement)
    membres = [m for m in ctx.guild.members if role in m.roles and not m.bot]
    if not membres:
        await ctx.send("Aucun membre n’a le rôle 'Club'.")
        return

    # Charger balances.json
    try:
        with open("balances.json", "r") as f:
            balances = json.load(f)
    except FileNotFoundError:
        balances = {}

    noms = []

    for membre in membres:
        user_id = str(membre.id)
        balances[user_id] = balances.get(user_id, 0) + montant
        if membre.display_name not in noms:
            noms.append(membre.display_name)

    # Sauvegarder balances.json
    with open("balances.json", "w") as f:
        json.dump(balances, f, indent=4)

    # Organiser les noms sur plusieurs lignes pour éviter les coupures
    lignes = [' / '.join(noms[i:i + 5]) for i in range(0, len(noms), 5)]
    noms_str = '\n'.join(lignes)

    await ctx.send(
        f"{montant}$ ont été donnés à tous les membres avec le rôle 'Club'.\nMembres concernés :\n{noms_str}"
    )


@bot.command()
async def listerclub(ctx):
    role = discord.utils.get(ctx.guild.roles, name="Club")
    if not role:
        await ctx.send("Le rôle 'Club' n'existe pas.")
        return

    membres = [
        m.display_name for m in ctx.guild.members
        if role in m.roles and not m.bot
    ]
    if not membres:
        await ctx.send("Aucun membre avec le rôle 'Club'.")
        return

    lignes = [' / '.join(membres[i:i + 5]) for i in range(0, len(membres), 5)]
    noms_str = '\n'.join(lignes)
    await ctx.send(f"Membres avec le rôle 'Club' :\n{noms_str}")


@bot.command()
async def debugclub(ctx):
    total_membres = len(ctx.guild.members)
    role = discord.utils.get(ctx.guild.roles, name="Club")
    if not role:
        await ctx.send("Rôle 'Club' introuvable.")
        return
    membres_club = [
        m.display_name for m in ctx.guild.members if role in m.roles
    ]
    await ctx.send(
        f"Total membres du serveur : {total_membres}\nMembres avec le rôle 'Club' : {len(membres_club)}\nListe : {', '.join(membres_club)}"
    )


# --- Gestion globale des erreurs de commande ---


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Il manque un ou plusieurs arguments dans ta commande.")
    elif isinstance(error, commands.BadArgument):
        await ctx.send(
            "Merci de vérifier les arguments fournis (type ou format incorrect)."
        )
    elif isinstance(error, commands.CommandNotFound):
        await ctx.send(
            "Commande inconnue. Tape !help pour voir la liste des commandes disponibles."
        )
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send("Tu n'as pas la permission d'utiliser cette commande.")
    elif isinstance(error, commands.MissingAnyRole):
        await ctx.send("❌ Tu n'as pas la permission d'utiliser cette commande."
                       )
    else:
        await ctx.send(
            "Une erreur est survenue lors de l'exécution de la commande.")
        print(f"Erreur non gérée dans {ctx.command}: {error}")


bot.run("TOKEN")
