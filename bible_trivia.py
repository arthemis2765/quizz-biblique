"""A multiple-choice Bible trivia game for the terminal.

Nouveautés dans cette version :
- Affichage du score en temps réel pendant la partie
- Sauvegarde des scores dans une base de données SQLite (scores.db)
- Classement (leaderboard) des meilleurs scores
- Interface terminal colorée et plus lisible
"""

import random
import sqlite3
import sys
from datetime import datetime
from pathlib import Path


# --------------------------------------------------------------------------
# Couleurs ANSI pour le terminal
# --------------------------------------------------------------------------
class Color:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"

    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    CYAN = "\033[96m"
    MAGENTA = "\033[95m"
    BLUE = "\033[94m"


def c(text, color):
    """Wrap text with an ANSI color code."""
    return f"{color}{text}{Color.RESET}"


# --------------------------------------------------------------------------
# Données du quiz
# --------------------------------------------------------------------------
QUESTIONS = [
    {"question": "Qui a construit l'arche avant le grand déluge ?", "options": ["Moïse", "Noé", "Abraham", "Élie"], "answer": "b", "category": "AT"},
    {"question": "Combien de jours et de nuits a-t-il plu pendant le déluge ?", "options": ["7", "12", "40", "100"], "answer": "c", "category": "AT"},
    {"question": "Qui a été avalé par un grand poisson ?", "options": ["Jonas", "Pierre", "Job", "Samson"], "answer": "a", "category": "AT"},
    {"question": "Quel jeune berger a vaincu le géant Goliath ?", "options": ["Saül", "Salomon", "Joseph", "David"], "answer": "d", "category": "AT"},
    {"question": "Qui a conduit les Israélites hors de l'esclavage en Égypte ?", "options": ["Josué", "Moïse", "Aaron", "Jacob"], "answer": "b", "category": "AT"},
    {"question": "Quel est le premier livre de la Bible ?", "options": ["Exode", "Genèse", "Psaumes", "Matthieu"], "answer": "b", "category": "AT"},
    {"question": "Qui a été jeté dans la fosse aux lions pour avoir prié Dieu ?", "options": ["Daniel", "Jérémie", "Ésaïe", "Ézéchiel"], "answer": "a", "category": "AT"},
    {"question": "Qui a été le premier homme créé par Dieu ?", "options": ["Abel", "Seth", "Caïn", "Adam"], "answer": "d", "category": "AT"},
    {"question": "Dans quelle ville Jésus est-il né ?", "options": ["Nazareth", "Jérusalem", "Bethléem", "Capharnaüm"], "answer": "c", "category": "NT"},
    {"question": "Combien de disciples Jésus a-t-il choisis ?", "options": ["7", "10", "12", "14"], "answer": "c", "category": "NT"},
    {"question": "Quel disciple a renié connaître Jésus trois fois ?", "options": ["Pierre", "Jean", "Thomas", "André"], "answer": "a", "category": "NT"},
    {"question": "Quelle nourriture Jésus a-t-il utilisée pour nourrir cinq mille personnes ?", "options": ["Du pain et du vin", "Cinq pains et deux poissons", "De la manne du ciel", "Des figues et du miel"], "answer": "b", "category": "NT"},
    {"question": "Quel disciple a trahi Jésus pour trente pièces d'argent ?", "options": ["Judas Iscariote", "Matthieu", "Philippe", "Jacques"], "answer": "a", "category": "NT"},
    {"question": "Quel est le verset le plus court de la Bible ?", "options": ["Dieu est amour.", "Jésus pleura.", "Priez sans cesse.", "Réjouissez-vous toujours."], "answer": "b", "category": "NT"},
    {"question": "Sur le chemin de quelle ville Paul s'est-il converti ?", "options": ["Rome", "Corinthe", "Damas", "Éphèse"], "answer": "c", "category": "NT"},
    {"question": "Qui est le père de la nation d'Israël, appelé « ami de Dieu » ?", "options": ["Abraham", "Isaac", "Jacob", "Moïse"], "answer": "a", "category": "PH"},
    {"question": "Quel patriarche a lutté toute une nuit avec un ange et a reçu le nom « Israël » ?", "options": ["Esaü", "Jacob", "Joseph", "Ruben"], "answer": "b", "category": "PH"},
    {"question": "Quel héros biblique a tué un lion à mains nues avant d'affronter les Philistins ?", "options": ["David", "Samson", "Gédéon", "Saül"], "answer": "b", "category": "PH"},
    {"question": "Quelle femme a caché les espions israélites à Jéricho ?", "options": ["Rahab", "Ruth", "Esther", "Déborah"], "answer": "a", "category": "PH"},
    {"question": "Quelle femme juge a dirigé Israël et conseillé le général Barak ?", "options": ["Miriam", "Déborah", "Esther", "Anne"], "answer": "b", "category": "PH"},
    {"question": "Qui a vaincu l'armée madianite avec seulement 300 hommes ?", "options": ["Josué", "Gédéon", "Samson", "Saül"], "answer": "b", "category": "PH"},
    {"question": "Quelle reine a risqué sa vie pour sauver son peuple en Perse ?", "options": ["Esther", "Ruth", "Judith", "Anne"], "answer": "a", "category": "PH"},
    {"question": "Quel roi est connu pour sa grande sagesse et pour avoir construit le Temple de Jérusalem ?", "options": ["David", "Salomon", "Roboam", "Ezéchias"], "answer": "b", "category": "PH"},
    {"question": "Qui a interprété les rêves de Pharaon et est devenu gouverneur d'Égypte ?", "options": ["Benjamin", "Ruben", "Joseph", "Juda"], "answer": "c", "category": "PH"},
    {"question": "Quel prophète a été enlevé au ciel dans un char de feu ?", "options": ["Élisée", "Élie", "Ésaïe", "Jérémie"], "answer": "b", "category": "PH"},
    {"question": "Qui a fait tomber les murailles de Jéricho en en faisant le tour avec le peuple ?", "options": ["Caleb", "Josué", "Aaron", "Moïse"], "answer": "b", "category": "PH"},
    {"question": "Quelle femme moabite est restée fidèle à sa belle-mère Naomi ?", "options": ["Ruth", "Orpa", "Noémi", "Rachel"], "answer": "a", "category": "PH"},
    {"question": "Qui a tout perdu mais est resté fidèle à Dieu malgré une immense souffrance ?", "options": ["Job", "Jonas", "Daniel", "Abraham"], "answer": "a", "category": "PH"},
    {"question": "Quel prophète a hérité du manteau et de l'esprit d'Élie ?", "options": ["Élie", "Élisée", "Amos", "Osée"], "answer": "b", "category": "PH"},
    {"question": "Qui a conduit le peuple juif dans la reconstruction des murailles de Jérusalem ?", "options": ["Esdras", "Néhémie", "Zorobabel", "Josias"], "answer": "b", "category": "PH"},
    {"question": "Quel prêtre-scribe a lu la Loi au peuple après le retour d'exil ?", "options": ["Esdras", "Néhémie", "Malachie", "Aggée"], "answer": "a", "category": "PH"},
    {"question": "Qui a été le premier roi d'Israël, choisi par le prophète Samuel ?", "options": ["David", "Saül", "Samuel", "Jonathan"], "answer": "b", "category": "PH"},
    {"question": "Quel fils du roi Saül a formé une amitié fidèle avec David ?", "options": ["Absalom", "Jonathan", "Salomon", "Amnon"], "answer": "b", "category": "PH"},
    {"question": "Quelle prophétesse a chanté un cantique de victoire après la traversée de la mer Rouge ?", "options": ["Miriam", "Séphora", "Rachel", "Léa"], "answer": "a", "category": "PH"},
    {"question": "Qui a été désigné pour parler à Pharaon à la place de Moïse, à cause de son éloquence ?", "options": ["Aaron", "Josué", "Caleb", "Nadab"], "answer": "a", "category": "PH"},
    {"question": "Quel espion, avec Josué, a rapporté un bon rapport sur la terre promise ?", "options": ["Caleb", "Guershom", "Éléazar", "Pinehas"], "answer": "a", "category": "PH"},
    {"question": "Qui a entendu la voix de Dieu l'appeler pendant son sommeil dans le tabernacle ?", "options": ["Samuel", "Éli", "Saül", "Nathan"], "answer": "a", "category": "PH"},
    {"question": "Quel apôtre était surnommé « le Rocher » par Jésus ?", "options": ["André", "Pierre", "Jacques", "Jean"], "answer": "b", "category": "PH"},
    {"question": "Qui, après avoir persécuté les chrétiens, est devenu l'un des plus grands apôtres ?", "options": ["Barnabas", "Silas", "Paul", "Timothée"], "answer": "c", "category": "PH"},
    {"question": "Quel disciple bien-aimé de Jésus a écrit un évangile et le livre de l'Apocalypse ?", "options": ["Jean", "Matthieu", "Marc", "Luc"], "answer": "a", "category": "PH"},
    {"question": "Quel homme a baptisé Jésus dans le Jourdain ?", "options": ["Jean-Baptiste", "Pierre", "André", "Philippe"], "answer": "a", "category": "PH"},
    {"question": "Quelle femme a été choisie par Dieu pour être la mère de Jésus ?", "options": ["Elisabeth", "Marie", "Marthe", "Marie-Madeleine"], "answer": "b", "category": "PH"},
    {"question": "Quel homme riche a offert son propre tombeau pour la sépulture de Jésus ?", "options": ["Nicodème", "Joseph d'Arimathée", "Simon de Cyrène", "Lazare"], "answer": "b", "category": "PH"},
    {"question": "Quel jeune compagnon de Paul a reçu deux épîtres qui portent son nom ?", "options": ["Tite", "Timothée", "Silas", "Épaphras"], "answer": "b", "category": "PH"},
    {"question": "Quel lévite a vendu son champ pour aider les apôtres, gagnant le surnom « fils d'encouragement » ?", "options": ["Étienne", "Philippe", "Barnabas", "Apollos"], "answer": "c", "category": "PH"},
    {"question": "Combien de plaies Dieu envoie-t-Il sur l'Égypte avant que Pharaon ne libère les Israélites ?", "options": ["7", "10", "12", "3"], "answer": "b", "category": "AT"},
    {"question": "Sur quelle montagne Moïse reçoit-il les Dix Commandements ?", "options": ["Le mont Sinaï", "Le mont Ararat", "Le mont Nébo", "Le mont Carmel"], "answer": "a", "category": "AT"},
    {"question": "Quel objet sacré contient les tables de la Loi, un pot de manne et le bâton d'Aaron ?", "options": ["L'arche de l'alliance", "Le chandelier d'or", "L'autel des parfums", "Le voile du sanctuaire"], "answer": "a", "category": "AT"},
    {"question": "Combien de commandements Dieu donne-t-il à Moïse sur le mont Sinaï ?", "options": ["7", "10", "12", "40"], "answer": "b", "category": "AT"},
    {"question": "Quelle nourriture miraculeuse Dieu envoie-t-il chaque matin aux Israélites dans le désert ?", "options": ["La manne", "Les cailles", "Le pain", "Le miel"], "answer": "a", "category": "AT"},
    {"question": "Combien de jours les Israélites font-ils le tour de Jéricho avant que ses murailles ne s'effondrent ?", "options": ["3", "7", "12", "40"], "answer": "b", "category": "AT"},
    {"question": "Sous quel roi le royaume d'Israël se divise-t-il en deux, Israël et Juda ?", "options": ["Roboam", "Salomon", "David", "Achab"], "answer": "a", "category": "AT"},
    {"question": "Quel empire déporte les habitants du royaume du Nord, Israël, en 722 av. J.-C. ?", "options": ["L'Assyrie", "Babylone", "L'Égypte", "La Perse"], "answer": "a", "category": "AT"},
    {"question": "Quel empire détruit le Temple de Jérusalem et déporte le peuple de Juda ?", "options": ["Babylone", "L'Assyrie", "La Perse", "La Grèce"], "answer": "a", "category": "AT"},
    {"question": "Quel roi perse autorise le retour des Juifs d'exil et la reconstruction du Temple ?", "options": ["Cyrus", "Darius", "Xerxès", "Assurbanipal"], "answer": "a", "category": "AT"},
    {"question": "Quel livre de la Bible relate la création du monde en six jours ?", "options": ["La Genèse", "L'Exode", "Job", "Les Psaumes"], "answer": "a", "category": "AT"},
    {"question": "Quel est le nom du jardin où Dieu place Adam et Ève ?", "options": ["Éden", "Canaan", "Goshen", "Sinaï"], "answer": "a", "category": "AT"},
    {"question": "Quel fils d'Adam et Ève tue son frère Abel ?", "options": ["Caïn", "Seth", "Hénoc", "Lémec"], "answer": "a", "category": "AT"},
    {"question": "Quel oiseau Noé envoie-t-il et qui revient avec un rameau d'olivier, signe que les eaux se retirent ?", "options": ["Une colombe", "Un corbeau", "Un aigle", "Une hirondelle"], "answer": "a", "category": "AT"},
    {"question": "Quel signe Dieu place-t-il dans le ciel après le déluge, en symbole de son alliance ?", "options": ["L'arc-en-ciel", "Une étoile", "Un nuage", "Le soleil"], "answer": "a", "category": "AT"},
    {"question": "Quelle tour les hommes tentent-ils de construire pour atteindre le ciel, provoquant la confusion des langues ?", "options": ["La tour de Babel", "La tour de Siloé", "Le temple de Salomon", "La citadelle de David"], "answer": "a", "category": "AT"},
    {"question": "De quelle ville Abraham part-il pour rejoindre la terre promise ?", "options": ["Ur", "Babylone", "Ninive", "Damas"], "answer": "a", "category": "AT"},
    {"question": "Dans quel pays Joseph devient-il gouverneur après avoir interprété les rêves de Pharaon ?", "options": ["L'Égypte", "Canaan", "Madian", "L'Assyrie"], "answer": "a", "category": "AT"},
    {"question": "Combien d'années de famine Joseph prédit-il en Égypte ?", "options": ["7", "10", "3", "40"], "answer": "a", "category": "AT"},
    {"question": "Quelle mer les Israélites traversent-ils à pied sec en fuyant l'Égypte ?", "options": ["La mer Rouge", "La mer Morte", "La mer de Galilée", "La Méditerranée"], "answer": "a", "category": "AT"},
    {"question": "Quel livre biblique détaille les lois sur les sacrifices et la pureté rituelle d'Israël ?", "options": ["Le Lévitique", "Les Nombres", "Le Deutéronome", "Josué"], "answer": "a", "category": "AT"},
    {"question": "Combien de tribus composent le peuple d'Israël ?", "options": ["10", "12", "7", "40"], "answer": "b", "category": "AT"},
    {"question": "Quelle tribu d'Israël est mise à part pour le service du sanctuaire, sans territoire propre ?", "options": ["Lévi", "Juda", "Benjamin", "Éphraïm"], "answer": "a", "category": "AT"},
    {"question": "Quel livre biblique raconte l'histoire d'un homme juste qui perd tout mais reste fidèle à Dieu ?", "options": ["Job", "Ruth", "Esther", "Jonas"], "answer": "a", "category": "AT"},
    {"question": "Quel roi d'Israël est réputé pour sa sagesse, illustrée par le jugement entre deux femmes se disputant un enfant ?", "options": ["Salomon", "David", "Saül", "Ézéchias"], "answer": "a", "category": "AT"},
    {"question": "Combien de proverbes le roi Salomon aurait-il composés, selon la tradition biblique ?", "options": ["3000", "500", "100", "10000"], "answer": "a", "category": "AT"},
    {"question": "Combien de temps faut-il, selon la Bible, pour construire le Temple de Salomon ?", "options": ["7 ans", "10 ans", "3 ans", "40 ans"], "answer": "a", "category": "AT"},
    {"question": "Quel livre de la Bible est un recueil de poèmes et de prières attribués en grande partie à David ?", "options": ["Les Psaumes", "Les Proverbes", "L'Ecclésiaste", "Le Cantique des cantiques"], "answer": "a", "category": "AT"},
    {"question": "Quel psaume commence par « L'Éternel est mon berger, je ne manquerai de rien » ?", "options": ["Le Psaume 23", "Le Psaume 1", "Le Psaume 51", "Le Psaume 100"], "answer": "a", "category": "AT"},
    {"question": "Quel livre, attribué à Salomon, s'ouvre sur « Vanité des vanités, tout est vanité » ?", "options": ["L'Ecclésiaste", "Les Proverbes", "Le Cantique des cantiques", "Les Psaumes"], "answer": "a", "category": "AT"},
    {"question": "À quelle ville Dieu envoie-t-il le prophète Jonas prêcher la repentance ?", "options": ["Ninive", "Babylone", "Tyr", "Damas"], "answer": "a", "category": "AT"},
    {"question": "Quel prophète voit une vision de la vallée des ossements desséchés qui reprennent vie ?", "options": ["Ézéchiel", "Ésaïe", "Jérémie", "Daniel"], "answer": "a", "category": "AT"},
    {"question": "Quel prophète est surnommé « le prophète pleureur » à cause de ses lamentations sur Jérusalem ?", "options": ["Jérémie", "Ésaïe", "Amos", "Osée"], "answer": "a", "category": "AT"},
    {"question": "Quel livre biblique porte le nom d'un prophète qui épouse une femme infidèle, en symbole de l'infidélité d'Israël ?", "options": ["Osée", "Joël", "Amos", "Michée"], "answer": "a", "category": "AT"},
    {"question": "Quel prophète annonce que le Messie naîtrait à Bethléem ?", "options": ["Michée", "Malachie", "Aggée", "Sophonie"], "answer": "a", "category": "AT"},
    {"question": "Quel est le dernier livre de l'Ancien Testament dans la Bible chrétienne ?", "options": ["Malachie", "Zacharie", "Aggée", "Abdias"], "answer": "a", "category": "AT"},
    {"question": "Combien de livres compte l'Ancien Testament dans la Bible protestante ?", "options": ["39", "27", "66", "46"], "answer": "a", "category": "AT"},
    {"question": "Quel peuple s'empare de l'arche de l'alliance lors d'une bataille contre Israël ?", "options": ["Les Philistins", "Les Assyriens", "Les Babyloniens", "Les Égyptiens"], "answer": "a", "category": "AT"},
    {"question": "Combien de temps Samson juge-t-il Israël, selon le livre des Juges ?", "options": ["20 ans", "40 ans", "12 ans", "7 ans"], "answer": "a", "category": "AT"},
    {"question": "Quel livre biblique suit celui des Juges et raconte l'histoire d'une femme moabite fidèle à sa belle-mère ?", "options": ["Ruth", "Esther", "1 Samuel", "Josué"], "answer": "a", "category": "AT"},
    {"question": "Dans le livre d'Esther, quel est le nom du premier ministre perse qui complote pour exterminer les Juifs ?", "options": ["Haman", "Mardochée", "Assuérus", "Memucan"], "answer": "a", "category": "AT"},
    {"question": "Quel roi perse épouse Esther et devient ainsi, indirectement, le sauveur du peuple juif ?", "options": ["Assuérus", "Cyrus", "Darius", "Nabuchodonosor"], "answer": "a", "category": "AT"},
    {"question": "Quel patriarche voit en songe une échelle reliant la terre au ciel, avec des anges y montant et descendant ?", "options": ["Jacob", "Abraham", "Isaac", "Joseph"], "answer": "a", "category": "AT"},
    {"question": "Combien d'années Jacob doit-il travailler pour Laban avant d'épouser Rachel ?", "options": ["7 ans", "14 ans", "3 ans", "20 ans"], "answer": "a", "category": "AT"},
    {"question": "Combien de pièces d'argent les frères de Joseph reçoivent-ils pour le vendre ?", "options": ["20", "30", "10", "40"], "answer": "a", "category": "AT"},
    {"question": "Quel est le nom de la terre promise aux descendants d'Abraham ?", "options": ["Canaan", "L'Égypte", "Madian", "Aram"], "answer": "a", "category": "AT"},
    {"question": "Quelle ville David conquiert-il pour en faire la capitale de son royaume ?", "options": ["Jérusalem", "Hébron", "Béthel", "Silo"], "answer": "a", "category": "AT"},
    {"question": "Quel fils de David se révolte contre son père et meurt suspendu par les cheveux dans un arbre ?", "options": ["Absalom", "Amnon", "Salomon", "Adonija"], "answer": "a", "category": "AT"},
    {"question": "Quel livre biblique décrit la construction du tabernacle, la tente où Dieu rencontre son peuple dans le désert ?", "options": ["L'Exode", "Le Lévitique", "Les Nombres", "Le Deutéronome"], "answer": "a", "category": "AT"},
    {"question": "Quel est le nom du fleuve que les Israélites traversent à pied sec pour entrer en terre promise, sous la conduite de Josué ?", "options": ["Le Jourdain", "Le Nil", "L'Euphrate", "Le Tigre"], "answer": "a", "category": "AT"},
    {"question": "Combien de temps Jésus jeûne-t-il dans le désert avant d'être tenté par le diable ?", "options": ["40 jours", "7 jours", "3 jours", "12 jours"], "answer": "a", "category": "NT"},
    {"question": "Quel est le premier miracle de Jésus, accompli lors d'un mariage à Cana ?", "options": ["L'eau changée en vin", "La multiplication des pains", "La guérison d'un aveugle", "La marche sur l'eau"], "answer": "a", "category": "NT"},
    {"question": "Comment appelle-t-on le célèbre discours de Jésus contenant les Béatitudes ?", "options": ["Le Sermon sur la montagne", "Le Sermon sur la plaine", "La parabole du semeur", "Le discours des Oliviers"], "answer": "a", "category": "NT"},
    {"question": "Dans quelle ville Jésus grandit-il, après son enfance en Égypte ?", "options": ["Nazareth", "Bethléem", "Capharnaüm", "Jérusalem"], "answer": "a", "category": "NT"},
    {"question": "Sur quelle montagne, selon la tradition, Jésus est-il transfiguré devant Pierre, Jacques et Jean ?", "options": ["Le mont Thabor", "Le mont Sinaï", "Le mont des Oliviers", "Le mont Carmel"], "answer": "a", "category": "NT"},
    {"question": "Quel apôtre marche sur l'eau vers Jésus avant de commencer à couler par manque de foi ?", "options": ["Pierre", "André", "Jean", "Jacques"], "answer": "a", "category": "NT"},
    {"question": "Combien de lépreux Jésus guérit-il en une seule fois, dont un seul revient le remercier ?", "options": ["10", "7", "12", "5"], "answer": "a", "category": "NT"},
    {"question": "Quel homme riche et petit de taille grimpe sur un sycomore pour voir Jésus passer ?", "options": ["Zachée", "Nicodème", "Lazare", "Barthélemy"], "answer": "a", "category": "NT"},
    {"question": "Quel ami de Jésus, mort depuis quatre jours, est ressuscité à Béthanie ?", "options": ["Lazare", "Jaïrus", "Zachée", "Étienne"], "answer": "a", "category": "NT"},
    {"question": "Quelle femme oint les pieds de Jésus avec un parfum précieux et les essuie avec ses cheveux ?", "options": ["Marie de Béthanie", "Marthe", "Salomé", "Jeanne"], "answer": "a", "category": "NT"},
    {"question": "Quel jour de la semaine Jésus est-il crucifié, selon la tradition chrétienne ?", "options": ["Vendredi", "Jeudi", "Dimanche", "Samedi"], "answer": "a", "category": "NT"},
    {"question": "Sur quelle colline, à l'extérieur de Jérusalem, Jésus est-il crucifié ?", "options": ["Le Golgotha", "Le mont des Oliviers", "Le mont Sion", "Le mont Moriah"], "answer": "a", "category": "NT"},
    {"question": "Quel jour Jésus ressuscite-t-il d'entre les morts, selon les Évangiles ?", "options": ["Le troisième jour", "Le septième jour", "Le premier jour du jeûne", "Quarante jours après"], "answer": "a", "category": "NT"},
    {"question": "Combien de jours Jésus ressuscité apparaît-il à ses disciples avant de monter au ciel ?", "options": ["40 jours", "7 jours", "3 jours", "50 jours"], "answer": "a", "category": "NT"},
    {"question": "Quel événement, cinquante jours après Pâques, voit le Saint-Esprit descendre sur les apôtres à Jérusalem ?", "options": ["La Pentecôte", "La Transfiguration", "L'Ascension", "La Nativité"], "answer": "a", "category": "NT"},
    {"question": "Quel est le nom du premier martyr chrétien, lapidé pour sa foi selon le livre des Actes ?", "options": ["Étienne", "Jacques", "Barnabé", "Philippe"], "answer": "a", "category": "NT"},
    {"question": "Quel centurion romain est, avec sa famille, parmi les premiers non-Juifs à recevoir le baptême chrétien ?", "options": ["Corneille", "Pilate", "Félix", "Festus"], "answer": "a", "category": "NT"},
    {"question": "Quel évangéliste écrit aussi le livre des Actes des Apôtres, en plus de son évangile ?", "options": ["Luc", "Marc", "Matthieu", "Jean"], "answer": "a", "category": "NT"},
    {"question": "Combien d'évangiles compte le Nouveau Testament ?", "options": ["4", "3", "5", "2"], "answer": "a", "category": "NT"},
    {"question": "Quel évangile est considéré comme le plus court et le plus rapide dans son récit ?", "options": ["Marc", "Matthieu", "Luc", "Jean"], "answer": "a", "category": "NT"},
    {"question": "Quel évangile met l'accent sur la divinité de Jésus, en commençant par « Au commencement était la Parole » ?", "options": ["Jean", "Marc", "Matthieu", "Luc"], "answer": "a", "category": "NT"},
    {"question": "Quel évangile s'adresse surtout à un public juif et met en avant l'accomplissement des prophéties ?", "options": ["Matthieu", "Marc", "Luc", "Jean"], "answer": "a", "category": "NT"},
    {"question": "Quel apôtre écrit la majorité des épîtres du Nouveau Testament ?", "options": ["Paul", "Pierre", "Jean", "Jacques"], "answer": "a", "category": "NT"},
    {"question": "Dans quelle ville l'apôtre Paul prêche-t-il devant l'Aréopage, un tribunal philosophique ?", "options": ["Athènes", "Corinthe", "Éphèse", "Rome"], "answer": "a", "category": "NT"},
    {"question": "Quelle épître de Paul est adressée aux chrétiens de la capitale de l'Empire romain ?", "options": ["Romains", "Éphésiens", "Colossiens", "Galates"], "answer": "a", "category": "NT"},
    {"question": "Quel livre du Nouveau Testament contient les visions apocalyptiques de Jean sur l'île de Patmos ?", "options": ["L'Apocalypse", "Les Actes", "Les Hébreux", "Jude"], "answer": "a", "category": "NT"},
    {"question": "Combien de lettres aux Églises ouvrent le livre de l'Apocalypse ?", "options": ["7", "12", "3", "10"], "answer": "a", "category": "NT"},
    {"question": "Quel roi juif ordonne le massacre des enfants de Bethléem après la naissance de Jésus ?", "options": ["Hérode le Grand", "Hérode Antipas", "Hérode Agrippa", "Ponce Pilate"], "answer": "a", "category": "NT"},
    {"question": "Quel gouverneur romain juge Jésus et autorise sa crucifixion, malgré ses doutes sur sa culpabilité ?", "options": ["Ponce Pilate", "Hérode Antipas", "Félix", "Festus"], "answer": "a", "category": "NT"},
    {"question": "Quel disciple refuse de croire à la résurrection de Jésus tant qu'il n'a pas vu ses blessures ?", "options": ["Thomas", "Philippe", "André", "Barthélemy"], "answer": "a", "category": "NT"},
    {"question": "Quel apôtre est décapité sur ordre du roi Hérode Agrippa Ier, selon le livre des Actes ?", "options": ["Jacques, fils de Zébédée", "Jean", "André", "Philippe"], "answer": "a", "category": "NT"},
    {"question": "De quelle ville partent Paul et Barnabas pour leur premier voyage missionnaire ?", "options": ["Antioche", "Jérusalem", "Éphèse", "Rome"], "answer": "a", "category": "NT"},
    {"question": "Quel métier exerçait l'apôtre Paul pour subvenir à ses besoins durant ses voyages missionnaires ?", "options": ["Fabricant de tentes", "Pêcheur", "Charpentier", "Collecteur d'impôts"], "answer": "a", "category": "NT"},
    {"question": "Quel métier Pierre et André exerçaient-ils avant de suivre Jésus ?", "options": ["Pêcheurs", "Bergers", "Charpentiers", "Agriculteurs"], "answer": "a", "category": "NT"},
    {"question": "Quel métier Matthieu exerçait-il avant de devenir disciple de Jésus ?", "options": ["Collecteur d'impôts", "Pêcheur", "Médecin", "Scribe"], "answer": "a", "category": "NT"},
    {"question": "Quel évangéliste est aussi décrit comme médecin dans les épîtres de Paul ?", "options": ["Luc", "Marc", "Matthieu", "Jean"], "answer": "a", "category": "NT"},
    {"question": "Quelle parabole de Jésus raconte l'histoire d'un fils qui dilapide son héritage puis revient chez son père ?", "options": ["Le fils prodigue", "Le bon Samaritain", "La brebis perdue", "Le semeur"], "answer": "a", "category": "NT"},
    {"question": "Quelle parabole met en scène un voyageur secouru par un étranger, après avoir été ignoré par un prêtre et un lévite ?", "options": ["Le bon Samaritain", "Le fils prodigue", "Les talents", "Le grain de moutarde"], "answer": "a", "category": "NT"},
    {"question": "Combien de paniers de morceaux restent après que Jésus a nourri cinq mille personnes ?", "options": ["12 paniers", "7 paniers", "5 paniers", "2 paniers"], "answer": "a", "category": "NT"},
    {"question": "En plus d'un bruit de vent violent, quel signe visible se pose sur chaque apôtre lors de la Pentecôte ?", "options": ["Des langues de feu", "Une colombe", "Un tremblement de terre", "Un nuage lumineux"], "answer": "a", "category": "NT"},
    {"question": "Quel fils d'Abraham est presque sacrifié sur le mont Moriah avant qu'un ange n'arrête son père ?", "options": ["Isaac", "Ismaël", "Jacob", "Ésaü"], "answer": "a", "category": "PH"},
    {"question": "Quelle est la femme d'Abraham qui rit en apprenant qu'elle aura un fils dans sa vieillesse ?", "options": ["Sarah", "Hagar", "Rebecca", "Milca"], "answer": "a", "category": "PH"},
    {"question": "Quelle est la servante égyptienne de Sarah qui devient la mère d'Ismaël ?", "options": ["Hagar", "Zilpa", "Bilha", "Ruth"], "answer": "a", "category": "PH"},
    {"question": "Quelle femme est choisie comme épouse d'Isaac après avoir offert de l'eau à un serviteur et à ses chameaux ?", "options": ["Rebecca", "Rachel", "Léa", "Sarah"], "answer": "a", "category": "PH"},
    {"question": "Quel frère jumeau de Jacob vend son droit d'aînesse pour un plat de lentilles ?", "options": ["Ésaü", "Ruben", "Juda", "Benjamin"], "answer": "a", "category": "PH"},
    {"question": "Quelle est l'épouse préférée de Jacob, pour laquelle il travaille sept ans chez Laban ?", "options": ["Rachel", "Léa", "Bilha", "Zilpa"], "answer": "a", "category": "PH"},
    {"question": "Quelle est la première épouse de Jacob, donnée à lui par ruse à la place de Rachel ?", "options": ["Léa", "Rachel", "Dina", "Tamar"], "answer": "a", "category": "PH"},
    {"question": "Quel est le nom du plus jeune fils de Jacob, frère de Joseph, né de Rachel ?", "options": ["Benjamin", "Ruben", "Lévi", "Dan"], "answer": "a", "category": "PH"},
    {"question": "Quel est le nom du fils aîné de Jacob et de Léa ?", "options": ["Ruben", "Siméon", "Lévi", "Juda"], "answer": "a", "category": "PH"},
    {"question": "De quel fils de Jacob la tribu et le royaume de Juda tirent-ils leur nom ?", "options": ["Juda", "Ruben", "Benjamin", "Lévi"], "answer": "a", "category": "PH"},
    {"question": "Quel neveu d'Abraham s'échappe de la ville de Sodome avant sa destruction ?", "options": ["Lot", "Ismaël", "Nachor", "Haran"], "answer": "a", "category": "PH"},
    {"question": "Quel est le premier juge mentionné dans le livre des Juges, neveu de Caleb ?", "options": ["Othniel", "Éhud", "Shamgar", "Jephté"], "answer": "a", "category": "PH"},
    {"question": "Quel juge gaucher d'Israël tue le roi moabite Églon avec une épée cachée ?", "options": ["Éhud", "Othniel", "Jephté", "Tola"], "answer": "a", "category": "PH"},
    {"question": "Quel juge d'Israël fait un vœu imprudent qui lui coûte le sacrifice de sa fille ?", "options": ["Jephté", "Éhud", "Gédéon", "Samson"], "answer": "a", "category": "PH"},
    {"question": "Quelle femme stérile prie ardemment au tabernacle de Silo pour obtenir un fils, qui deviendra le prophète Samuel ?", "options": ["Anne", "Déborah", "Miriam", "Ruth"], "answer": "a", "category": "PH"},
    {"question": "Quel grand prêtre de Silo élève le jeune Samuel au tabernacle ?", "options": ["Éli", "Aaron", "Éléazar", "Phinées"], "answer": "a", "category": "PH"},
    {"question": "Quel roi d'Israël est décrit comme « un homme selon le cœur de Dieu » ?", "options": ["David", "Saül", "Salomon", "Josaphat"], "answer": "a", "category": "PH"},
    {"question": "Quel fils de Salomon perd dix tribus d'Israël à cause de sa dureté envers le peuple ?", "options": ["Roboam", "Jéroboam", "Abija", "Asa"], "answer": "a", "category": "PH"},
    {"question": "Quel est le premier roi du royaume du Nord, Israël, après la division du royaume ?", "options": ["Jéroboam", "Roboam", "Achab", "Omri"], "answer": "a", "category": "PH"},
    {"question": "Quel roi d'Israël épouse Jézabel et introduit le culte de Baal dans le royaume ?", "options": ["Achab", "Jéroboam", "Omri", "Achazia"], "answer": "a", "category": "PH"},
    {"question": "Quelle reine, épouse d'Achab, fait tuer les prophètes de l'Éternel et persécute Élie ?", "options": ["Jézabel", "Athalie", "Esther", "Vasthi"], "answer": "a", "category": "PH"},
    {"question": "Quel roi de Juda, réputé pour sa piété, remporte une victoire miraculeuse sans combattre en louant Dieu ?", "options": ["Josaphat", "Ézéchias", "Josias", "Asa"], "answer": "a", "category": "PH"},
    {"question": "Quel roi de Juda voit sa vie prolongée de quinze ans après une prière fervente au prophète Ésaïe ?", "options": ["Ézéchias", "Josias", "Manassé", "Ozias"], "answer": "a", "category": "PH"},
    {"question": "Quel jeune roi de Juda relance la réforme religieuse après la découverte du livre de la Loi dans le Temple ?", "options": ["Josias", "Ézéchias", "Joas", "Amon"], "answer": "a", "category": "PH"},
    {"question": "Quel roi de Juda, réputé très impie, se repent après avoir été emmené captif à Babylone ?", "options": ["Manassé", "Achaz", "Amon", "Joachim"], "answer": "a", "category": "PH"},
    {"question": "Quel roi de Babylone détruit Jérusalem et emmène le peuple juif en exil ?", "options": ["Nabuchodonosor", "Balthazar", "Cyrus", "Darius"], "answer": "a", "category": "PH"},
    {"question": "Quel grand prophète annonce la naissance d'un enfant appelé « Emmanuel » et décrit un serviteur souffrant ?", "options": ["Ésaïe", "Jérémie", "Ézéchiel", "Daniel"], "answer": "a", "category": "PH"},
    {"question": "Quel prophète est jeté dans une citerne boueuse pour avoir annoncé la chute de Jérusalem ?", "options": ["Jérémie", "Ésaïe", "Amos", "Michée"], "answer": "a", "category": "PH"},
    {"question": "Quel prophète, exilé à Babylone, voit une vision de roues dans les airs et de créatures célestes ?", "options": ["Ézéchiel", "Daniel", "Jérémie", "Abdias"], "answer": "a", "category": "PH"},
    {"question": "Quel prophète interprète le rêve d'une statue aux pieds d'argile pour le roi Nabuchodonosor ?", "options": ["Daniel", "Ézéchiel", "Ésaïe", "Jérémie"], "answer": "a", "category": "PH"},
    {"question": "Quels trois compagnons de Daniel sont jetés dans une fournaise ardente pour avoir refusé d'adorer une statue d'or ?", "options": ["Chadrak, Méshak et Abed-Nego", "Pierre, Jacques et Jean", "Aaron, Éléazar et Ithamar", "Gad, Nathan et Asaph"], "answer": "a", "category": "PH"},
    {"question": "Quel prophète épouse Gomer, une femme infidèle, en symbole de la relation entre Dieu et Israël ?", "options": ["Osée", "Joël", "Amos", "Michée"], "answer": "a", "category": "PH"},
    {"question": "Quel prophète, simple berger de Tekoa, dénonce les injustices sociales et l'hypocrisie religieuse d'Israël ?", "options": ["Amos", "Osée", "Joël", "Abdias"], "answer": "a", "category": "PH"},
    {"question": "Quel général syrien est guéri de la lèpre après s'être baigné sept fois dans le Jourdain, sur les conseils d'Élisée ?", "options": ["Naaman", "Ben-Hadad", "Hazaël", "Rezin"], "answer": "a", "category": "PH"},
    {"question": "Quel prophète païen voit son ânesse parler pour l'empêcher de maudire Israël ?", "options": ["Balaam", "Balak", "Éliphaz", "Bildad"], "answer": "a", "category": "PH"},
    {"question": "Quel lévite mène une rébellion contre Moïse et Aaron, avant que la terre ne s'ouvre pour l'engloutir ?", "options": ["Coré", "Dathan", "Abiram", "Nadab"], "answer": "a", "category": "PH"},
    {"question": "Quelle sœur de Moïse est frappée de lèpre pour s'être opposée à son mariage avec une Éthiopienne ?", "options": ["Miriam", "Séphora", "Rebecca", "Élisabeth"], "answer": "a", "category": "PH"},
    {"question": "Quels fils d'Aaron meurent après avoir offert un feu étranger devant l'Éternel ?", "options": ["Nadab et Abihu", "Éléazar et Ithamar", "Pinehas et Nadab", "Coré et Dathan"], "answer": "a", "category": "PH"},
    {"question": "Quel petit-fils d'Aaron est loué pour son zèle après avoir arrêté une plaie en Israël ?", "options": ["Pinehas", "Éléazar", "Ithamar", "Nadab"], "answer": "a", "category": "PH"},
    {"question": "Quelle femme tue le général cananéen Sisera en lui enfonçant un piquet de tente dans la tempe ?", "options": ["Yaël", "Déborah", "Rahab", "Miriam"], "answer": "a", "category": "PH"},
    {"question": "Quel général israélite conduit l'armée contre Sisera, sur les conseils de la prophétesse Déborah ?", "options": ["Barak", "Gédéon", "Éhud", "Jephté"], "answer": "a", "category": "PH"},
    {"question": "Quelle femme philistine trahit Samson en découvrant le secret de sa force ?", "options": ["Dalila", "Rahab", "Yaël", "Ruth"], "answer": "a", "category": "PH"},
    {"question": "Quel propriétaire de champ épouse Ruth la Moabite et devient son rédempteur ?", "options": ["Booz", "Élimélek", "Mahlon", "Kilion"], "answer": "a", "category": "PH"},
    {"question": "Quel est le nom du père du roi David ?", "options": ["Jessé", "Obed", "Booz", "Salmon"], "answer": "a", "category": "PH"},
    {"question": "Quelle femme intelligente empêche David de se venger de son mari Nabal, puis devient son épouse après la mort de celui-ci ?", "options": ["Abigaïl", "Bethsabée", "Mical", "Ahinoam"], "answer": "a", "category": "PH"},
    {"question": "Quelle femme, épouse d'Urie puis de David, devient la mère du roi Salomon ?", "options": ["Bethsabée", "Abigaïl", "Mical", "Ahinoam"], "answer": "a", "category": "PH"},
    {"question": "Quel mari de Bethsabée est envoyé délibérément en première ligne pour y mourir, sur ordre du roi David ?", "options": ["Urie le Hittite", "Joab", "Absalom", "Amasa"], "answer": "a", "category": "PH"},
    {"question": "Quel prophète confronte le roi David après son péché avec Bethsabée, au moyen d'une parabole ?", "options": ["Nathan", "Gad", "Samuel", "Ésaïe"], "answer": "a", "category": "PH"},
    {"question": "Quel fils infirme de Jonathan reçoit la bonté du roi David en mémoire de son amitié avec son père ?", "options": ["Mephiboshet", "Absalom", "Adonija", "Ischbaal"], "answer": "a", "category": "PH"},
    {"question": "Quelle reine étrangère rend visite à Salomon pour éprouver sa sagesse avec des énigmes ?", "options": ["La reine de Saba", "Athalie", "Vasthi", "Jézabel"], "answer": "a", "category": "PH"},
    {"question": "Quel prophète est nourri par des corbeaux près du torrent de Kerith durant une sécheresse ?", "options": ["Élie", "Élisée", "Samuel", "Ésaïe"], "answer": "a", "category": "PH"},
    {"question": "Quelle veuve voit sa farine et son huile ne jamais s'épuiser, grâce au prophète Élie ?", "options": ["La veuve de Sarepta", "La veuve de Naïn", "Anne", "Ruth"], "answer": "a", "category": "PH"},
    {"question": "Quel serviteur du prophète Élisée est frappé de lèpre pour avoir menti afin d'obtenir de l'argent de Naaman ?", "options": ["Guéhazi", "Ovadia", "Josaphat", "Élisée lui-même"], "answer": "a", "category": "PH"},
    {"question": "Quelle reine usurpatrice de Juda fait tuer sa propre famille royale pour s'emparer du trône ?", "options": ["Athalie", "Jézabel", "Vasthi", "Esther"], "answer": "a", "category": "PH"},
    {"question": "Quel jeune roi de Juda est caché pendant six ans dans le Temple avant d'être couronné à sept ans ?", "options": ["Joas", "Josias", "Ézéchias", "Amatsia"], "answer": "a", "category": "PH"},
    {"question": "Quel pharisien vient trouver Jésus de nuit pour l'interroger sur la nouvelle naissance ?", "options": ["Nicodème", "Gamaliel", "Caïphe", "Anne"], "answer": "a", "category": "PH"},
    {"question": "Quelle sœur de Marie et de Lazare se plaint d'être seule à servir pendant que sa sœur écoute Jésus ?", "options": ["Marthe", "Marie-Madeleine", "Salomé", "Jeanne"], "answer": "a", "category": "PH"},
    {"question": "Quelle femme, délivrée de sept démons par Jésus, est la première à voir le Christ ressuscité ?", "options": ["Marie-Madeleine", "Marthe", "Marie de Béthanie", "Jeanne"], "answer": "a", "category": "PH"},
    {"question": "Quel homme est réquisitionné pour porter la croix de Jésus jusqu'au Golgotha ?", "options": ["Simon de Cyrène", "Joseph d'Arimathée", "Nicodème", "Barabbas"], "answer": "a", "category": "PH"},
    {"question": "Quel prisonnier est libéré par Pilate à la place de Jésus, à la demande de la foule ?", "options": ["Barabbas", "Simon de Cyrène", "Malchus", "Caïphe"], "answer": "a", "category": "PH"},
    {"question": "Quel grand prêtre juif préside le procès religieux de Jésus avant sa remise à Pilate ?", "options": ["Caïphe", "Anne", "Gamaliel", "Nicodème"], "answer": "a", "category": "PH"},
    {"question": "Quel roi fait décapiter Jean-Baptiste, à la demande de la fille d'Hérodiade ?", "options": ["Hérode Antipas", "Hérode le Grand", "Hérode Agrippa", "Ponce Pilate"], "answer": "a", "category": "PH"},
    {"question": "Quelle jeune fille danse devant Hérode et demande la tête de Jean-Baptiste sur un plateau, à l'instigation de sa mère ?", "options": ["Salomé", "Hérodiade", "Bérénice", "Drusille"], "answer": "a", "category": "PH"},
    {"question": "Quelle est la mère de Jean-Baptiste, cousine de Marie, mère de Jésus ?", "options": ["Élisabeth", "Anne", "Marthe", "Salomé"], "answer": "a", "category": "PH"},
    {"question": "Quel prêtre, père de Jean-Baptiste, devient muet après avoir douté de l'annonce de l'ange Gabriel ?", "options": ["Zacharie", "Éli", "Caïphe", "Anne"], "answer": "a", "category": "PH"},
    {"question": "Quel vieillard, au Temple, prend l'enfant Jésus dans ses bras et loue Dieu de pouvoir enfin mourir en paix ?", "options": ["Siméon", "Nicodème", "Joseph d'Arimathée", "Gamaliel"], "answer": "a", "category": "PH"},
    {"question": "Quelle prophétesse âgée, présente au Temple, reconnaît elle aussi Jésus comme le Messie ?", "options": ["Anne", "Élisabeth", "Marthe", "Salomé"], "answer": "a", "category": "PH"},
    {"question": "Qui suit une étoile depuis l'Orient pour venir adorer l'enfant Jésus et lui offrir de l'or, de l'encens et de la myrrhe ?", "options": ["Les mages", "Les bergers", "Les prêtres du Temple", "Les scribes"], "answer": "a", "category": "PH"},
    {"question": "Quel frère de Simon Pierre est l'un des premiers disciples appelés par Jésus ?", "options": ["André", "Jacques", "Jean", "Philippe"], "answer": "a", "category": "PH"},
    {"question": "Quels deux frères pêcheurs, fils de Zébédée, sont surnommés « fils du tonnerre » par Jésus ?", "options": ["Jacques et Jean", "Pierre et André", "Philippe et Barthélemy", "Thomas et Matthieu"], "answer": "a", "category": "PH"},
    {"question": "Quel disciple invite Nathanaël à venir voir Jésus, en lui disant « Viens et vois » ?", "options": ["Philippe", "André", "Thomas", "Jacques"], "answer": "a", "category": "PH"},
    {"question": "Quel disciple Jésus décrit-il comme « un véritable Israélite, en qui il n'y a point de fraude » ?", "options": ["Nathanaël", "Thomas", "Matthieu", "Philippe"], "answer": "a", "category": "PH"},
    {"question": "Quel apôtre de Jésus est surnommé « le Zélote », en référence à son engagement politique antérieur ?", "options": ["Simon le Zélote", "Jude Thaddée", "Matthias", "Barthélemy"], "answer": "a", "category": "PH"},
    {"question": "Quel apôtre, aussi appelé Thaddée, écrit une courte épître mettant en garde contre les faux docteurs ?", "options": ["Jude", "Jacques", "Matthias", "Barthélemy"], "answer": "a", "category": "PH"},
    {"question": "Quel évangéliste baptise un haut fonctionnaire éthiopien qui lisait le livre d'Ésaïe sur la route de Gaza ?", "options": ["Philippe l'évangéliste", "Étienne", "Barnabas", "Silas"], "answer": "a", "category": "PH"},
    {"question": "Quel disciple de Damas est envoyé par Dieu pour rendre la vue à Saul de Tarse après sa conversion ?", "options": ["Ananias", "Étienne", "Barnabas", "Silas"], "answer": "a", "category": "PH"},
    {"question": "Quel compagnon de Paul chante des hymnes avec lui en prison à Philippes, avant qu'un tremblement de terre ne libère leurs chaînes ?", "options": ["Silas", "Timothée", "Tite", "Marc"], "answer": "a", "category": "PH"},
    {"question": "Quel collaborateur de Paul est laissé en Crète pour y organiser les Églises, et reçoit une épître à son nom ?", "options": ["Tite", "Timothée", "Silas", "Épaphras"], "answer": "a", "category": "PH"},
    {"question": "Quel couple, fabricants de tentes comme Paul, l'accompagne dans son ministère à Corinthe et à Éphèse ?", "options": ["Priscille et Aquilas", "Marthe et Marie", "Lydie et Tabitha", "Élisabeth et Zacharie"], "answer": "a", "category": "PH"},
    {"question": "Quel prédicateur éloquent d'Alexandrie est instruit plus précisément dans la foi par Priscille et Aquilas ?", "options": ["Apollos", "Épaphras", "Tychique", "Trophime"], "answer": "a", "category": "PH"},
    {"question": "Quel jeune assistant abandonne Paul et Barnabas en cours de voyage missionnaire, provoquant plus tard leur séparation ?", "options": ["Jean-Marc", "Tite", "Silas", "Timothée"], "answer": "a", "category": "PH"},
    {"question": "Quelle marchande de pourpre est la première convertie de Paul en Europe, à Philippes ?", "options": ["Lydie", "Priscille", "Tabitha", "Chloé"], "answer": "a", "category": "PH"},
    {"question": "Quel collaborateur de Paul fonde l'Église de Colosses et prie ardemment pour elle ?", "options": ["Épaphras", "Apollos", "Tychique", "Onésime"], "answer": "a", "category": "PH"},
    {"question": "Quel esclave fugitif, converti par Paul, est renvoyé à son maître Philémon avec une lettre d'intercession ?", "options": ["Onésime", "Épaphras", "Tychique", "Trophime"], "answer": "a", "category": "PH"},
    {"question": "Quel est le nom de la reine d'Israël dont l'orgueil pousse le roi Assuérus à la répudier avant qu'Esther ne devienne reine ?", "options": ["Vasthi", "Athalie", "Jézabel", "Michal"], "answer": "a", "category": "PH"},
    {"question": "Quel cousin d'Esther l'élève et refuse de se prosterner devant Haman ?", "options": ["Mardochée", "Haman", "Assuérus", "Memucan"], "answer": "a", "category": "PH"},
    {"question": "Quel roi d'Assyrie envoie Rabshaké insulter Dieu devant les murs de Jérusalem, avant d'être vaincu par un ange ?", "options": ["Sanchérib", "Salmanazar", "Tiglath-Piléser", "Assarhaddon"], "answer": "a", "category": "PH"},
    {"question": "Quel prêtre courageux cache et protège le jeune roi Joas pendant six ans contre la reine Athalie ?", "options": ["Yehoyada", "Zacharie", "Éli", "Hilkija"], "answer": "a", "category": "PH"},
    {"question": "Quel grand prêtre retrouve le livre de la Loi perdu dans le Temple, sous le règne de Josias ?", "options": ["Hilkija", "Yehoyada", "Éléazar", "Phinées"], "answer": "a", "category": "PH"},
    {"question": "Quel scribe et prêtre lit publiquement la Loi de Moïse au peuple, après le retour d'exil à Jérusalem ?", "options": ["Esdras", "Néhémie", "Zorobabel", "Josué le grand prêtre"], "answer": "a", "category": "PH"},
    {"question": "Quel descendant de David dirige le premier groupe d'exilés revenus de Babylone pour reconstruire le Temple ?", "options": ["Zorobabel", "Esdras", "Néhémie", "Josias"], "answer": "a", "category": "PH"},
    {"question": "Quel échanson du roi perse obtient l'autorisation de retourner reconstruire les murailles de Jérusalem ?", "options": ["Néhémie", "Esdras", "Zorobabel", "Mardochée"], "answer": "a", "category": "PH"},
    {"question": "Quel général en chef de l'armée de David tue Absalom malgré l'ordre du roi de l'épargner ?", "options": ["Joab", "Abner", "Amasa", "Benaja"], "answer": "a", "category": "PH"},
    {"question": "Quel puissant guerrier de David commande sa garde personnelle et tue un lion dans une citerne un jour de neige ?", "options": ["Benaja", "Joab", "Abischaï", "Éléazar"], "answer": "a", "category": "PH"},
    {"question": "Quel devin moabite est engagé par le roi Balak pour maudire le peuple d'Israël en marche vers Canaan ?", "options": ["Balaam", "Job", "Éliphaz", "Agur"], "answer": "a", "category": "PH"},
    {"question": "Quel homme au grand patrimoine perd tous ses biens et ses enfants, mais reste intègre malgré les épreuves envoyées par Satan ?", "options": ["Job", "Naboth", "Onésime", "Lazare"], "answer": "a", "category": "PH"},
    {"question": "Quel roi d'Israël fait assassiner Naboth pour s'emparer de sa vigne ?", "options": ["Achab", "Jéroboam", "Omri", "Achazia"], "answer": "a", "category": "PH"},
    {"question": "Quel espion, envoyé avec Josué explorer Canaan, reçoit en récompense la ville d'Hébron pour sa fidélité ?", "options": ["Caleb", "Guershom", "Éléazar", "Nadab"], "answer": "a", "category": "PH"},
    {"question": "Quel beau-père de Moïse, prêtre de Madian, lui conseille de déléguer la justice à d'autres chefs ?", "options": ["Jéthro", "Réuel", "Hobab", "Balaam"], "answer": "a", "category": "PH"},
    {"question": "Quel apôtre remplace Judas Iscariote après sa mort, choisi par tirage au sort parmi les disciples ?", "options": ["Matthias", "Barnabas", "Silas", "Apollos"], "answer": "a", "category": "PH"},
]

LETTERS = ["a", "b", "c", "d"]

CATEGORY_LABELS = {
    "AT": "Ancien Testament",
    "NT": "Nouveau Testament",
    "PH": "Personnages & Héros",
    "MIX": "Mixte (toutes les questions)",
}

DB_PATH = Path(__file__).resolve().parent / "scores.db"


def questions_for_category(category):
    """Return the questions matching a category code, or all of them for MIX."""
    if category == "MIX":
        return QUESTIONS
    return [q for q in QUESTIONS if q.get("category") == category]


# --------------------------------------------------------------------------
# Base de données
# --------------------------------------------------------------------------
def init_db():
    """Create the scores table if it doesn't already exist."""
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS scores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                player_name TEXT NOT NULL,
                score INTEGER NOT NULL,
                total_questions INTEGER NOT NULL,
                played_at TEXT NOT NULL
            )
            """
        )
        conn.commit()


def save_score(player_name, score, total_questions):
    """Persist one game result in the database."""
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            INSERT INTO scores (player_name, score, total_questions, played_at)
            VALUES (?, ?, ?, ?)
            """,
            (player_name, score, total_questions, datetime.now().isoformat(timespec="seconds")),
        )
        conn.commit()


def get_leaderboard(limit=10):
    """Return the best scores, ranked by percentage then by score."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute(
            """
            SELECT player_name, score, total_questions, played_at
            FROM scores
            ORDER BY (CAST(score AS REAL) / total_questions) DESC, score DESC, played_at DESC
            LIMIT ?
            """,
            (limit,),
        )
        return cursor.fetchall()


def get_player_history(player_name, limit=5):
    """Return the most recent games for a given player."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute(
            """
            SELECT score, total_questions, played_at
            FROM scores
            WHERE player_name = ?
            ORDER BY played_at DESC
            LIMIT ?
            """,
            (player_name, limit),
        )
        return cursor.fetchall()


# --------------------------------------------------------------------------
# Logique du quiz
# --------------------------------------------------------------------------
def print_header(title):
    width = max(len(title) + 4, 40)
    print()
    print(c("=" * width, Color.CYAN))
    print(c(title.center(width), Color.CYAN + Color.BOLD))
    print(c("=" * width, Color.CYAN))


def ask_question(number, total, item, running_score):
    """Ask one question and return True if the answer was correct."""
    print(f"\n{c(f'Question {number}/{total}', Color.BLUE + Color.BOLD)}"
          f"   {c(f'Score actuel : {running_score}', Color.DIM)}")
    print(c(item["question"], Color.BOLD))

    for letter, option in zip(LETTERS, item["options"]):
        print(f"  {c(letter + ')', Color.YELLOW)} {option}")

    while True:
        answer = input(c("Ta réponse (a/b/c/d) : ", Color.MAGENTA)).strip().lower()
        if answer in LETTERS:
            break
        print(c("Réponds avec a, b, c ou d, s'il te plaît.", Color.RED))

    if answer == item["answer"]:
        print(c("✓ Correct !", Color.GREEN + Color.BOLD))
        return True

    correct_index = LETTERS.index(item["answer"])
    correct_option = item["options"][correct_index]
    print(c(f"✗ Pas tout à fait. La bonne réponse était "
            f"{item['answer']}) {correct_option}.", Color.RED))
    return False


def show_final_score(player_name, score, total):
    """Print the final score with a short closing message."""
    percentage = round(100 * score / total)

    print_header("RÉSULTAT FINAL")
    print(f"{player_name}, tu as obtenu "
          f"{c(f'{score}/{total}', Color.BOLD)} "
          f"({c(f'{percentage}%', Color.YELLOW)})")

    if score == total:
        message = "Score parfait ! Tu connais vraiment bien ta Bible."
        color = Color.GREEN
    elif score >= total * 0.8:
        message = "Excellent travail ! Il ne t'a manqué que quelques questions."
        color = Color.GREEN
    elif score >= total * 0.5:
        message = "Pas mal du tout. Encore un peu de lecture et tu vas tout déchirer."
        color = Color.YELLOW
    else:
        message = "Bon essai ! Chaque question ratée est une histoire à redécouvrir."
        color = Color.RED

    print(c(message, color))


def show_leaderboard():
    """Display the top scores stored in the database."""
    rows = get_leaderboard()
    print_header("CLASSEMENT DES MEILLEURS SCORES")

    if not rows:
        print(c("Aucune partie enregistrée pour le moment.", Color.DIM))
        return

    print(f"{'#':<3} {'Joueur':<20} {'Score':<10} {'%':<6} {'Date'}")
    print(c("-" * 55, Color.DIM))
    for i, (name, score, total, played_at) in enumerate(rows, start=1):
        pct = round(100 * score / total)
        date_str = played_at.split("T")[0]
        rank_color = Color.YELLOW if i == 1 else Color.RESET
        print(c(f"{i:<3} {name:<20} {score}/{total:<7} {pct:<6} {date_str}", rank_color))


def choose_category():
    """Ask the player which category of questions to play, and return its code."""
    print_header("CHOISIS UNE CATÉGORIE")
    codes = ["AT", "NT", "PH", "MIX"]
    for i, code in enumerate(codes, start=1):
        count = len(questions_for_category(code))
        print(f"{i}) {c(CATEGORY_LABELS[code], Color.CYAN)} "
              f"{c(f'({count} questions)', Color.DIM)}")

    while True:
        choice = input(c("\nChoix : ", Color.MAGENTA)).strip()
        if choice in ("1", "2", "3", "4"):
            return codes[int(choice) - 1]
        print(c("Choix invalide, réessaie.", Color.RED))


def choose_question_count(available):
    """Ask how many questions to play, capped by what's available."""
    default = min(10, available)
    while True:
        raw = input(
            c(f"\nCombien de questions veux-tu jouer ? (1-{available}, "
              f"Entrée pour {default}) : ", Color.MAGENTA)
        ).strip()
        if not raw:
            return default
        if raw.isdigit() and 1 <= int(raw) <= available:
            return int(raw)
        print(c(f"Entre un nombre entre 1 et {available}.", Color.RED))


def run_quiz(player_name):
    """Run one full game and save the result."""
    category = choose_category()
    pool = questions_for_category(category)
    if not pool:
        print(c("Aucune question dans cette catégorie pour le moment.", Color.RED))
        return

    count = choose_question_count(len(pool))

    # Copie profonde pour ne jamais modifier la banque de questions globale
    questions = [
        {"question": q["question"], "options": q["options"].copy(), "answer": q["answer"]}
        for q in random.sample(pool, count)
    ]
    # Mélange aussi l'ordre des options affichées pour chaque question
    for item in questions:
        pairs = list(zip(LETTERS, item["options"]))
        correct_option = item["options"][LETTERS.index(item["answer"])]
        random.shuffle(pairs)
        item["options"] = [opt for _, opt in pairs]
        item["answer"] = LETTERS[[opt for _, opt in pairs].index(correct_option)]

    total = len(questions)
    score = 0
    for number, item in enumerate(questions, start=1):
        if ask_question(number, total, item, score):
            score += 1

    show_final_score(player_name, score, total)
    save_score(player_name, score, total)


def main_menu():
    print_header("BIBLE TRIVIA QUIZ")
    print(f"1) {c('Jouer', Color.GREEN)}")
    print(f"2) {c('Voir le classement', Color.CYAN)}")
    print(f"3) {c('Quitter', Color.RED)}")
    return input(c("\nChoix : ", Color.MAGENTA)).strip()


def main():
    init_db()
    player_name = input(c("Quel est ton prénom ? ", Color.MAGENTA)).strip() or "Joueur"

    while True:
        choice = main_menu()

        if choice == "1":
            run_quiz(player_name)
        elif choice == "2":
            show_leaderboard()
        elif choice == "3":
            print(c("\nMerci d'avoir joué, à bientôt !", Color.CYAN))
            break
        else:
            print(c("Choix invalide, réessaie.", Color.RED))


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(c("\n\nMerci d'avoir joué !", Color.CYAN))
        sys.exit(0)