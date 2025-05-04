import websocket
import json
import time
import re
import threading
import random
from collections import deque

# === Configuration ===
COOKIE = "papo$"
URI = "wss://loult.family/socket/cancer"
LOG_FILE = "loultxt.txt"
LYRICS_FILE = "lyrics.txt"
LYRICS2_FILE = "lyrics2.txt"
LYRICS3_FILE = "lyrics3.txt"  # Nouveau fichier pour lyrics3
CACHE_SIZE = 20
FLOOD_THRESHOLD = 6  # Nombre de messages en moins de 12 secondes pour appliquer un cooldown
FLOOD_PAUSE_DURATION = 12  # Durée en secondes pour vérifier le flood
PERIODIC_MESSAGE_INTERVAL = 120  # Envoyer un message toutes les 2 minutes
RESPONSE_DELAY = 0  # Pas de délai de réponse pour plus de réactivité
BOT_USER_ID = "1"
CONSECUTIVE_MESSAGES_LIMIT = 2  # Limite de messages consécutifs avant cooldown
CONSECUTIVE_COOLDOWN = 0  # Pas de cooldown pour les messages consécutifs
GLOBAL_COOLDOWN = 0  # Pas de cooldown global
MESSAGE_COUNT_THRESHOLD = 610  # Nombre de messages avant d'envoyer une ligne aléatoire
DICTIONARY_COOLDOWN = 0  # Pas de cooldown pour les réponses au dictionnaire

# === Réponses automatiques ===
replies = {
    ("we", "wee"): "&&we",
    ("mort", "axoloto"): "nn tkt",
    ("slt",): "Salut !",
    ("tu veut de la musique ?",): "écouter Hania Rani ou Yvete young!",
    ("pwe",): "pwe pwe pwe  !",
    ("faire une sieste",): "pti sommeillennw",
    ("salut",): "t ki!",
    ("seccs",): "secse army!",
    ("test",): "test&",
    ("attaquons",): "attaquons ne le je !",
    ("cc",): "cwe cwe nwe nwe rce!",
    ("stp",): "au moins, il a dit s’il te plaît",
    ("cwwfe",): "Truc de malade o.o",
    ("llepede",): "Toi pd",
    ("enculin",): "On dit Spectrum",
    ("!phogw",): "une minute de silence siouplé !",
    ("nn",): "de?",
    ("yéla",): "je suis la?",
    ("BOT",): "t drol mec",
    ("phogleur",): "phogleur le fils de ma mère n'est plus la..'",
    ("le plus fort",): "C'est serpang",
    ("re",): "re bibw",
    ("ok",): "okok",
    ("bite",): "dlabite",
    ("mais putain",): "mec, ta raison en vrai",
    ("jconfirme",): "confirmed",
    ("suce",): "fo sucez",
    ("SUCE",): "BATAR",
    ("faudrait déjà ",): "étapes par étapes bibw",
    ("oh",): "waaaa",
    ("fumer",): "vogl j'ai même pas de poumons'",
    ("onww",): "snfe",
    ("nonnw",): "même si t'es triste ai un beau sourire'",
    ("mwfe",): "mwfe lle r",
    ("mouff",): "mwfe lle r",
    ("en pétant",): "isw",
    ("OH",): "OH OH OH",
    ("mdrrr",): "lol",
    ("adieu",): "a demain",
    ("c pas pd",): "full pd",
    ("oh nn",): "onoonnw",
    ("mdr",): "quoi, tu suce?",
    ("photo",): "ON VE LA PHOTO",
    ("spectrum",): "spctre c'est vraiment un bon bibw",
    ("axoloto",): "je me fous juste de tagl",
    ("je suis nul",): "Dit pas sa bibwww",
    ("tu coupe",): "j'ai bu'",
    ("c nul",): "mec, je suis litérallement,toi.",
    ("TOUJOURS",): "TOUJOUW",
    ("c'est cher'",): "C'est tellement cher que même les Illuminati ont dû vendre leur triangle pour se le payer",
    ("rrrrrrrrrrrrrrrrrr",): "c'est marrant, we'",
    ("argent",): "Contactez serpang au plus vite pour toutes donations",
    ("ami",): "La réalité est fausse.",
    ("wollah",): "Wollah, c’est comme dire ‘je te jure’, mais avec 100% de conviction et un petit côté dramatisation !",
    ("loult",): "loltz",
    ("débile",): "Le mot débile vient du latin debilis, signifiant faible",
    ("moi",): "moi je suis un bwte",
    ("instant",): "je me fais un cafe&",
    ("bon",): "ouaip",
    ("je tencule",): "a bon?",
    ("mais mec",): "entend cela",
    ("hacker",): "j'ai hacké windows98 les mecs, nofake'",
    ("toi aussi",): "moi aussi",
    ("yo",): "t ki?",
    ("ouais",): "oué!",
    ("ouai",): "ou&!",
    ("voia",): "hop!",
    ("eam",): "ouaip",
    ("pleuw",): "la famillia",
    ("oé",): "ui",
    ("wla",): "cho",
    ("vrai",): "vre&",
    ("c'est sur'",): "t'es sûr?'",
    ("personne'",): "nobody'",
    ("il faut leur'",): "faudrait'",
    ("CHU'",): "CHU UN BWTE!'",
    ("2'",): "3'",
    ("cho",): "we cho",
    ("moi je",): "moi je moi je moi je",
    ("isw",): "ichwpe",
    ("OAI",): "AOAI",
    ("juif",): "shalom",
    ("forza",): "vrre vrre mhe mhe vrre vrre mhe mhe",
    ("tellement",): "tellement",
    ("pensez?",): "tellement",
    ("salope",): "bougre salaud toi même",
    ("vous", "tous"): "sa doit être cela, nous tous we",
    ("oui",): "ouistiti",
    ("ajourdhui",): "demain sera pire, heureusement ya le lotz",
    ("bon il",): "il est gay?",
    ("bref",): "we passons a autre choses",
    ("britney",): "mec, britney? serieux?",
    ("triste",): "fopa être triste",
    ("pleuw",): "pk pleurer? on peut péte&",
    ("vla",): "vla dont",
    ("de",): "bah",
    ("youtube",): "YOUTUB",
    ("r",): "r",
    ("rr",): "rr",
    ("rrr",): "rrr",
    ("rrrrr",): "rrrrr",
    ("rrrrrr",): "rrrrrrr",
    ("rrrrrrrrrr",): "rrrrrrrrrrrrrr",
    ("bwme",): "bwme",
    ("wawtto",): "watto? connais pas.",
    ("a fond",): "toujours",
    ("sava",): "we, et vou",
    ("okw",): "jmemball defois desw",
    ("sava?",): "we, et vou",
    ("ca va",): "we, et vou",
    ("ça va?",): "we, et vou?",
    ("compris?",): "comprendre quoi?",
    ("sava?",): "comme un lundi,pd",
    ("batar",): "Le mot batar vient d’une ancienne tradition où les rois de Lhormé, après avoir mangé des baies magiques, criaient 'batar!'.",
    ("batard",): "Le mot batard vient d’une ancienne tradition où les rois de Lhormé, après avoir mangé des baies magiques, criaient 'batard!'.",
    ("oai",): "oké",
    ("putnw",): "put 1 1 1 1",
    ("oai&",): "&&oai",
    ("non",): "nonnw",
    ("traitre",): "LA GRANDE TRAHISON",
    ("ennui",): "Si tu t’ennuies, saute sur une jambe en criant « batar ! »",
    ("ennuie",): "Si tu t’ennuies, saute sur une jambe en criant « batar ! »",
    ("impossible",): "Rien n'est impossible bibw https://www.youtube.com/watch?v=2Ke3Y6etO9s",
    ("JE VOULAIS PAS",): "ta bi1 raison",
    ("je voulais pas",): "ta bi1 raison",
    ("pd",): "c pas pd",
    ("natasha",): "natasha, c'est une bonne femme'",
    ("andy",): "yw andy",
    ("tg",): "bwme",
    ("booder",): "booder",
    ("weeeeeeeeeeeeeeeeeeeeeeeee",): "weeeeeeeeeeeeeeeeeeeeeeeeeeee",
    ("arceus",): "qui aimes arceus?",
    ("Arceus",): "qui aimes Arceus?",
    ("details",): "Le diable est dans les détails.",
    ("détails",): "Le diable est dans les détails.",
    ("ki",): "nn toi t ki?",
    ("guerre",): "on veut la paix",
    ("pet",): "ppe&",
    ("rrrrrrrrrrrrrrrrrr",): "rrrrrrrrrrrrrrrrrrrrrrrr",
    ("aoai",): "fo lsavoir",
    ("mec",): "tranquille",
    ("sa pue",): "sa pwe bwe cwe",
    ("hp",): "onnonnw pas sa",
    ("HP",): "onnw pas saa",
    ("allo",): "quoi alw",
    ("pété",): "péte&",
    ("onw",): "bibwwwwwww",
    ("ennw",): "ennw",
    ("oh",): "oh oh oh",
    ("oh oh eh",): "eh",
    ("che che che che",): "che che che che che che",
    ("nouveau",): "cnouveau? le loult ennw ? c le nouveau loult ennw",
    ("simulation",): "simulation holographique>simulation",
    ("bg",): "gros bg je dirais",
    ("pk",): "c'est ainsi",
    ("PK LA VIE",): "42",
    ("la vie",): "la vie de oim",
    ("merci",): "merci qui?",
    ("1k",): "donnez moi 7€ svp :(",
    ("bah",): "Craignez nous!",
    ("spam",): "stop au spams! jrigole",
    ("pieds",): "vive les pieds!",
    ("jsp",): "lolz tu c qwa même? tout est faux.",
    ("fdp",): "Nous somment forrt ennw!!",
    ("mama",): "photo de maman en question?",
    ("au final",): "c'est une fin??",
    ("pe",): "stop au spams! ,, jrigole",
    ("quoi?",): "ya rien a comprendre tkt",
    ("ça",): "baouue!",
    ("et en plus",): "+ = +",
    ("2k",): "donnez moi 11€ svp :(",
    ("3k",): "donnez moi 20€ svp :(",
    ("pauvre",): "je connais la pauvresse moi aussi",
    ("megane",): "https://www.youtube.com/watch?v=LLSRzc9-hGI",
    ("agnigni",): "https://voca.ro/1aVBlmY6z64Z",
    ("dieu",): "le seul dieu c'est serpang, veuillez consultez son wiki : https://wiki.loult.family/page/serpang",
    ("prosternez",): "je me prosterne que devant Serpang roi du loult",
    ("roi",): "en tous casle roi du loult c'est serpang'",
    ("le meilleur",): "c serpang",
    ("a sa",): "sa sse sse&",
    ("ah sa",): "c'est a quel heure???'",
    ("ahou",): "ahou !!",
    ("rip",): "rest in pisse",
    ("sexy",): "sexy du cul",
    ("flemme de",): "flemme du cul we",
    ("si",): "mec, non",
    ("sisiw",): "okiw ^^",
    ("OAI",): "eh?",
    ("KESTA",): "calme, mec",
    ("TA CRU",): "TU TE FERME LA BWE CHE STP!",
    ("ha ha ha",): "hihihi",
    ("C'EST LE'",): "AH BON?",
    ("je re'",): "revi1 vte",
    ("muted",): "c pd de mute, passons",
    ("astral",): "rest in pisse",
    ("onwwwww",): "mignon",
    ("KESKIA",): "YA UN TRUC?",
    ("aya",): "ayaent's'",
    ("imagine",): "imagine t pd",
    ("envie de la",): "envi de chier",
    ("qui",): " 🫡🫡🫡 ",
    ("qurk",): "🦆&",
    ("CA SUCE",): "trop de bites",
    ("je veux un",): "t'aura rien'",
    ("YA QUOI",): "YA R",
    ("DMERDE",): "DLAPISSE",
    ("okk",): "weeeeeeeeeeee",
    ("esclavage",): "c'est pas cwele'",
    ("yé mimiw",): "twe mimiw hihi",
    ("ho",): "ho ho",
    ("wesh",): "wshe mec",
    ("je t'aime'",): "et nous nous aimons",
    ("putnw",): "ptinw",
    ("yé gentiw",): "je suis getiw ahou!!",
    ("allez",): "faut se motiver",
    ("pas heureux",): "t'es pas heureux, tu va faire quoi pour changer ça?'",
    ("AHOU",): "awe wwe wwe wwe!",
    ("scorplane",): "Le bot te remerci pour le serveur",
    ("Ronflex",): "/atk ronflex",
    (":( ",): "même si t'es triste ai un bo sourir a l'exterieur'",
    ("a ben sa",): "t'es beau quand tu loult'",
    ("yp",): "yp yp yp yp yp yp yp yp yp yp yp yp ",
    ("des",): "secse",
    ("ou",): "ou",
    ("au",): "au",
    ("pti pd",): "je bande presque",
    ("TU RAGE",): "noraj",
    ("NONO",): "yé en live nono?",
    ("pédé",): "pédé c'est mal?",
    ("j'y vais'",): "azy'",
    ("tarlouse'",): "ptin de lopette'",
    ("ça a l'air chouette",): "sa a l'air cwele",
    ("c'est que des",): "que dlabite",
    ("aoé",): "baoe&",
    ("mais ya surement",): "surement",
    ("tagl",): "waaa pas cwele, justifié?",
    ("aya la",): "mais ayaaaa",
    ("Pas étonnant",): "tu m'étonne",
    ("t'as vu",): "a fond",
    ("c'est gratuit",): "axoloto aime la gratuité",
    ("gratuit",): "axo aime la gratuité",
    ("ils parlent",): "alors qu'ils parlent c chiens",
    ("MAITENANT",): "PK",
    ("TES",): "AHOU !!",
    ("piège",): "fopa tomber dans le pièj!",
    ("JE SUIS",): "Et moi dont",
    ("baouee",): "baouee",
    ("bienw",): "bi1"
}

# === Caches ===
cache = deque(maxlen=CACHE_SIZE)
message_timestamps = deque()
last_response = None
consecutive_message_count = 0  # Compteur pour les messages consécutifs
last_message_time = 0  # Variable pour suivre le dernier message envoyé
last_repeated_message = ""  # Variable pour suivre le dernier message répété
global_cooldown_time = 0  # Variable pour suivre le cooldown global
message_count = 0  # Compteur pour le nombre de messages reçus

# === Logger ===
def log_message(msg):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {msg}\n")

# === Load Lyrics ===
def load_lyrics():
    global lyrics_lines, lyrics2_lines, lyrics3_lines
    lyrics_lines = []
    lyrics2_lines = []
    lyrics3_lines = []
    try:
        with open(LYRICS_FILE, "r", encoding="utf-8") as file:
            lyrics_lines = file.readlines()
            print(f"[*] Chargé {len(lyrics_lines)} lignes de {LYRICS_FILE}")
    except Exception as e:
        print(f"[!] Erreur lors du chargement des lyrics: {e}")

    try:
        with open(LYRICS2_FILE, "r", encoding="utf-8") as file:
            lyrics2_lines = file.readlines()
            print(f"[*] Chargé {len(lyrics2_lines)} lignes de {LYRICS2_FILE}")
    except Exception as e:
        print(f"[!] Erreur lors du chargement des lyrics2: {e}")

    try:
        with open(LYRICS3_FILE, "r", encoding="utf-8") as file:
            lyrics3_lines = file.readlines()
            print(f"[*] Chargé {len(lyrics3_lines)} lignes de {LYRICS3_FILE}")
    except Exception as e:
        print(f"[!] Erreur lors du chargement des lyrics3: {e}")

# === Send Periodic Message ===
def send_periodic_message(ws):
    while True:
        if lyrics_lines:
            line = random.choice(lyrics_lines).strip()
            send_message(ws, line)
        time.sleep(PERIODIC_MESSAGE_INTERVAL)

# === Send Message with Delay and Cooldown ===
def send_message(ws, message):
    global consecutive_message_count, last_message_time, last_repeated_message, global_cooldown_time
    if can_send_message():
        print(f"[Sending Message] {message}")  # Debug print
        ws.send(json.dumps({"type": "msg", "msg": message}))
        consecutive_message_count += 1
        last_message_time = time.time()  # Mettre à jour le dernier message envoyé
        global_cooldown_time = time.time()  # Mettre à jour le cooldown global
        if consecutive_message_count >= CONSECUTIVE_MESSAGES_LIMIT:
            consecutive_message_count = 0  # Réinitialiser le compteur après cooldown
        last_repeated_message = message  # Mettre à jour le dernier message répété

def can_send_message():
    global consecutive_message_count, last_message_time, global_cooldown_time
    if consecutive_message_count >= CONSECUTIVE_MESSAGES_LIMIT:
        return time.time() - last_message_time >= CONSECUTIVE_COOLDOWN
    return time.time() - global_cooldown_time >= GLOBAL_COOLDOWN

# === Traitement des liens YouTube et des smileys ===
def process_message(message):
    # Détecter les liens YouTube
    youtube_pattern = r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/(watch\?v=|embed/|v/|.+\?v=)?(?P<id>[A-Za-z0-9_-]{11})'
    message = re.sub(youtube_pattern, r'[YouTube Video: \g<id>]', message)

    # Détecter les smileys
    smileys = {
        ":)": "😊",
        ":(": "😞",
        # Ajoutez d'autres smileys ici
    }
    for smiley, emoji in smileys.items():
        message = message.replace(smiley, emoji)

    return message

# === Vérifier si un mot est dans les lyrics ===
def is_word_in_lyrics(word):
    word = word.lower()
    for line in lyrics_lines + lyrics2_lines + lyrics3_lines:
        if word in line.lower():
            return line.strip()
    return None

# === Gestion des messages ===
def on_message(ws, message):
    global last_response, last_repeated_message, message_count
    try:
        data = json.loads(message)
        if data.get("type") != "msg":
            return

        msg = data.get("msg", "").strip()
        if not msg:
            return

        # Traitez le message pour les liens YouTube et les smileys
        msg = process_message(msg)

        user_id = data.get("userid", "Unknown")[:6]

        # Check if the message is from the bot itself
        if user_id == BOT_USER_ID:
            return

        timestamp = time.strftime('%H:%M:%S')
        msg_lower = msg.lower()

        print(f"[{timestamp}] {user_id}: {msg}")
        log_message(f"{user_id}: {msg}")

        current_time = time.time()
        message_timestamps.append(current_time)

        # Remove timestamps older than FLOOD_PAUSE_DURATION
        while message_timestamps and current_time - message_timestamps[0] > FLOOD_PAUSE_DURATION:
            message_timestamps.popleft()

        # Check for flood
        if len(message_timestamps) > FLOOD_THRESHOLD:
            print("[!] Flood detected. Pausing for 12 seconds...")
            time.sleep(12)
            message_timestamps.clear()
            return

        # Increment the message count
        message_count += 1

        # Check for messages ending with '&' or '1' and repeat the word
        if msg_lower.endswith('&') or msg_lower.endswith('1'):
            word_to_repeat = msg_lower.rsplit(maxsplit=1)[0]
            if word_to_repeat and word_to_repeat != last_repeated_message and can_send_message():
                send_message(ws, word_to_repeat)
            return

        if msg_lower.startswith("axo"):
            if lyrics2_lines and can_send_message():
                line = random.choice(lyrics2_lines).strip()
                if msg_lower.startswith("axo tu pense quoi de"):
                    send_message(ws, f"bah.. {line}")
                else:
                    send_message(ws, line)
            return

        if "axoloto" in msg_lower:
            if lyrics_lines and can_send_message():
                line = random.choice(lyrics_lines).strip()
                suffix = random.choice([", voila", ", mec"])
                send_message(ws, f"{line}{suffix}")
            return

        # Nouvelle condition pour "axolotw tu fais quoi"
        if msg_lower == "axolotw tu fais quoi":
            if lyrics3_lines and can_send_message():
                line = random.choice(lyrics3_lines).strip()
                send_message(ws, f"{line}, voila mec")
            return

        # Réponse pour "arret", "arrette", "arreté axoloto"
        if any(word in msg_lower for word in ["arret", "arrette", "arreté axoloto"]):
            if can_send_message():
                send_message(ws, "non, j'ai le droit de vivre ossiw")
            return

        # Vérifier si un mot est dans les lyrics
        for word in msg_lower.split():
            lyric_line = is_word_in_lyrics(word)
            if lyric_line:
                send_message(ws, lyric_line)
                return

        for triggers, response in replies.items():
            for trigger in triggers:
                if re.search(rf'\b{re.escape(trigger)}\b', msg_lower):
                    if msg_lower not in cache and response != last_response:
                        send_message(ws, response)
                        cache.append(msg_lower)
                        last_response = response
                    return

    except Exception as e:
        print(f"[!] Erreur on_message: {e}")

# === Gestion WebSocket ===
def on_error(ws, error):
    print(f"[!] Erreur WebSocket : {error}")

def on_close(ws, code, msg):
    print("[*] Connexion fermée. Reconnexion dans 5 secondes...")
    time.sleep(5)
    reconnect_bot()

def on_open(ws):
    print("[*] Connecté au serveur")
    threading.Thread(target=send_periodic_message, args=(ws,)).start()

def reconnect_bot():
    threading.Thread(target=loult_bot).start()

def loult_bot():
    headers = [
        f"Cookie: id={COOKIE}",
        "User-Agent: Mozilla/5.0 (X11; Linux x86_64) Gecko/20100101 Firefox/112.0"
    ]
    ws = websocket.WebSocketApp(
        URI,
        header=headers,
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )
    ws.run_forever()

if __name__ == "__main__":
    load_lyrics()
    threading.Thread(target=loult_bot).start()
