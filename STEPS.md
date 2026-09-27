# Camagru — Plan de réalisation

## Stack technique retenue
- **Serveur** : Python 3, stdlib uniquement (pas de framework)
- **Base de données** : SQLite (`sqlite3`, stdlib)
- **Routing** : `wsgiref` (WSGI, PEP 3333) + `ThreadingMixIn` — tranché
- **Vues** : `string.Template` + échappement HTML automatique (cf. étape 2)
- **Frontend** : HTML/CSS/JS natif (aucun framework JS) + framework CSS *classless* sans JS (cf. étape 10)
- **Images** : encodeur/décodeur PNG maison (`struct`, `zlib`) — pas de Pillow.
  Le navigateur envoie des **pixels bruts** ; le serveur ne décode que ses propres calques (cf. étape 0.5)
- **Email dev** : `smtplib` + Mailpit en conteneur (Mailhog n'est plus maintenu)
- **Déploiement** : Docker / docker-compose, en place dès l'étape 0

---

## Séquence de démarrage

Transversale : chaque étape y ajoute un morceau, aucune ne la possède entièrement.
C'est ce que `python -m camagru` doit faire, dans cet ordre, à **chaque** lancement.

1. **Lire la configuration** — `os.environ` avec des valeurs par défaut *(étape 1, puis 3)*
2. **Initialiser la base** — `init()`, rendu inoffensif à la répétition par
   `CREATE TABLE IF NOT EXISTS` *(étape 1)*
3. **Décoder les calques** et garder leurs pixels en mémoire *(étapes 0.5 et 7)*
4. **Démarrer le serveur HTTP** *(étape 2)*

**Règle : tout se fait avant `make_server()`.** Si une étape échoue — base inaccessible,
calque invalide, variable manquante — le serveur ne démarre pas du tout, avec un message
clair. Mieux vaut un refus de démarrer qu'une application qui tombe à la première requête.

**Pourquoi c'est une contrainte, pas un confort** : le sujet impose un déploiement en une
commande. Le correcteur tapera `docker compose up` et rien d'autre — il ne connaît aucune
de tes commandes internes. Tout ce qui est nécessaire au fonctionnement du site doit donc
se produire ici.

Les points d'entrée manuels (`python -m camagru.db.init`) restent utiles, mais uniquement
comme outils de développement. Ils ne doivent jamais être un prérequis.

---

## Logique de l'ordre des étapes

Le projet se déroule en quatre temps. Connaître le temps dans lequel on se trouve évite de se
demander « à quoi sert ce que je fais ».

**1. Les fondations invisibles — étapes 0 à 1** ✅
Le setup, le codec PNG, le schéma de base. Rien à voir dans un navigateur, et c'est normal :
ce sont les briques dont tout le reste dépend, et celles qui auraient été les plus pénibles à
reprendre plus tard. C'est aussi le moment où le risque du projet se lève (le codec).

**2. Le squelette visible — étapes 1.5 et 2**
D'abord **tout le site en maquette**, cliquable de bout en bout, sans une ligne de Python.
Puis le serveur qui le sert aux vraies URL. Aucune fonctionnalité ne marche encore, mais le
projet se regarde et se montre.

**3. On remplit les pages — étapes 3 à 9**
Chaque étape rend vivante une page qui existe déjà : l'inscription, la connexion, la capture,
la galerie. On ne construit plus à l'aveugle, on branche.

**4. On finit — étapes 10 à 12**
Les ajustements responsive, la containerisation, la chasse aux bugs et aux warnings.

**Pourquoi la maquette (1.5) arrive si tôt** : elle ne dépend de rien. Des fichiers `.html` et
une feuille de style s'ouvrent dans un navigateur sans serveur. Et elle donne à l'étape 2 sa
spécification : la liste des URL à router, et le contenu réel des templates à rendre.

La sécurité (étape 5) échappe à ce découpage : ce n'est pas un temps du projet mais un ensemble
de règles à appliquer dès la première ligne de HTML et de SQL.

---

## Étape 0 — Setup projet

**Estimation : 3–5 h** — ✅ terminée
- Structure de dossiers : MVC en couches → `controllers/` → `services/` → `models/` → `views/`
  - Règle unique qui fait tenir l'ensemble : **aucune couche ne connaît celle au-dessus d'elle**.
    Pas de SQL dans un controller, pas de HTTP (requête, cookie, session) dans un service,
    pas de règle métier dans un model.
  - Test de validation : pouvoir appeler `services.user.register(...)` depuis un script CLI,
    sans serveur HTTP. Si c'est impossible, la logique a fui dans le controller.
- Environnement Python (`venv` / `uv`)
- `.gitignore` complet **avant le premier commit** : `.env`, `.venv/`, `__pycache__/`, `data/`
  - + `.env.example` versionné (les clés, pas les valeurs)
- `Dockerfile` + `docker-compose.yml` **dès maintenant** (app + Mailpit), pas à l'étape 11
  - Mailpit sert dès l'étape 3 (mail de confirmation) : SMTP sur le port 1025, interface web sur le port 8025
  - Le serveur Python doit écouter sur `0.0.0.0` : sur `127.0.0.1`, il est injoignable
    depuis l'extérieur du conteneur
  - Depuis le conteneur de l'app, le serveur SMTP s'appelle `mailpit` (nom du service compose),
    pas `localhost` → hôte SMTP lu depuis `.env`, pour pouvoir aussi lancer l'app hors conteneur
  - Les variables de `.env` arrivent dans `os.environ` via `env_file: .env`
- **Notions** : MVC en couches, front controller, `venv`, Dockerfile, docker-compose, réseau entre conteneurs

## Étape 0.5 — Proof of concept PNG

**Estimation : 5–8 h** — ✅ terminée
- **Principe retenu : le serveur ne décode jamais un fichier envoyé par un utilisateur.**
  - Le navigateur dessine la photo (webcam ou fichier) sur un `<canvas>` et envoie ses **pixels bruts**
    (cf. étape 6). Le décodeur PNG ne lit que les calques superposables, fichiers de confiance fournis avec le projet.
  - Pourquoi : une photo de téléphone est en JPEG, et un décodeur JPEG est hors de portée. Le passage par un
    `<canvas>` côté navigateur est donc obligatoire de toute façon ; autant envoyer directement ses pixels.
  - Pourquoi pas `canvas.toDataURL('image/png')` : la spec HTML impose le format PNG mais pas son contenu
    interne (type de couleur, filtres). `getImageData()`, lui, est spécifié : toujours RGBA, 8 bits, 4 octets par pixel.
- Préparer 3–4 calques : PNG **640×480, RGBA 8 bits, non entrelacés**, sticker déjà placé dans l'image
  (pas de redimensionnement ni de positionnement à coder côté serveur)
  - Ne pas les passer dans un optimiseur (TinyPNG, pngquant) : ils convertissent en palette
    (type de couleur 3), que le décodeur refusera
- **Décodeur** (calques uniquement) :
  - signature, IHDR en premier chunk, concaténation des IDAT, arrêt sur IEND
  - n'accepter que : type de couleur 6 (RGBA), profondeur 8, entrelacement 0, dimensions 640×480
  - gérer **les 5 filtres** de scanline : c'est le logiciel d'export qui les choisit, pas toi
  - décoder tous les calques **au démarrage du serveur** et garder les pixels en mémoire ;
    si un calque est invalide, refuser de démarrer avec un message clair
- **Encodeur** (image finale) : filtre None sur chaque ligne + `zlib.compress` + `crc32` par chunk
- Test : décoder un calque → ré-encoder → ouvrir le résultat dans un visualiseur d'images
- Performances mesurées en Python pur sur 640×480 : défiltrage Paeth ~0,7 s (pire cas, une fois au démarrage),
  fusion alpha ~0,2 s, encodage ~0,05 s → aucun problème
- **Notions** : structure d'un fichier PNG (signature, chunks IHDR/IDAT/IEND), `struct`, `zlib` (`decompress`/`compress`/`crc32`), filtres de scanline (None, Sub, Up, Average, Paeth)

## Étape 1 — Schéma de base de données

**Estimation : 2–3 h** — ✅ terminée
- Tables : users, images, likes, comments, sessions
- Données exigées par le mandatory, à prévoir **dès maintenant** pour ne pas retoucher le schéma plus tard :
  - `users` : compte confirmé ou non, token de confirmation, token de reset + date d'expiration,
    préférence de notification des commentaires en **`DEFAULT 1`** (le sujet : activée par défaut)
  - username et email `UNIQUE`
- Piège : les clés étrangères sont **désactivées par défaut** dans SQLite → `PRAGMA foreign_keys = ON`
  à chaque connexion, sinon `ON DELETE CASCADE` ne fait rien et supprimer une image laisse
  ses likes et commentaires orphelins
- **Notions** : `sqlite3`, conception relationnelle, clés étrangères, contraintes UNIQUE

## Étape 1.5 — Maquette HTML/CSS de tout le site

**Estimation : 3–4 h** — ✅ terminée — aucun Python, aucun serveur : des fichiers `.html` ouverts dans le navigateur

La première fois que le projet ressemble à un site. Toutes les pages, avec leur mise en page
définitive et des **données écrites en dur**. Tu double-cliques sur `galerie.html` et tu navigues.

- Les pages à écrire :
  - **Galerie** (accueil, publique) — 5 vignettes, compteurs de likes, commentaires
  - **Inscription**, **connexion**, **mot de passe oublié**, **nouveau mot de passe**
  - **Profil** — modification username / email / mot de passe, case de notification
  - **Édition** — preview webcam (un rectangle gris suffit), liste de calques, bouton de capture,
    barre latérale de miniatures
  - **404** et **403**
- Le header en deux variantes, dans deux pages différentes : connecté (profil, édition,
  déconnexion) et visiteur (connexion, inscription)
- Les liens pointent sur des noms de fichiers (`connexion.html`) — ils seront réécrits en URL
  à l'étape 2
- Framework CSS *classless* (Pico.css, Simple.css…) — autorisé par le sujet, aucun JavaScript
  - Les balises sémantiques sont stylées sans écrire une seule classe
  - Copier le fichier `.css` en local, ne pas dépendre d'un CDN
  - Compromis connu : ces frameworks reposent sur les variables CSS (Chrome ≥ 49), donc pas sur
    la compatibilité stricte Chrome ≥ 46 demandée par le sujet (cf. étape 12)

**Pourquoi maintenant** : à partir d'ici, chaque étape consiste à *remplir une page qui existe
déjà*, au lieu de construire à l'aveugle. Tu vois où tu vas, et tu peux montrer le projet.

**Deux bénéfices moins évidents.** En écrivant les pages, tu découvres :

- **la liste des URL de ton site** — en posant les liens du header et les `action=` des
  formulaires. Ton routeur de l'étape 2 aura une spécification concrète au lieu d'une liste imaginée ;
- **les données que chaque page réclame** — « il me faut le nombre de likes, et si *cet*
  utilisateur a liké ». Cette liste dictera les fonctions de `models/` et `services/`.

**Le piège à éviter** : ne pas peaufiner. Le but est la structure et la navigation, pas le design
final. Les ajustements viendront à l'étape 10, quand les pages seront réellement remplies.

✅ *Terminée quand* tu peux cliquer de page en page et parcourir tout le site dans ton navigateur.

## Étape 2 — Routing HTTP et rendu des vues

**Estimation : 7–11 h** — ✅ terminée — beaucoup de petites briques, peu de difficulté par brique
(dont ~1 h pour convertir les maquettes de l'étape 1.5 en templates)
- Dispatch des requêtes GET/POST vers des handlers
  - Pattern *front controller* : un seul point d'entrée qui route, pas un fichier par page
- **Rendu des vues : `string.Template` + échappement HTML automatique** (aucun moteur de templates à parser)
  - Une fonction `render(nom_template, raw=None, **valeurs)` d'une dizaine de lignes :
    - **toutes** les `valeurs` passent par `html.escape()` avant substitution ;
    - seul le dict `raw` est injecté tel quel, et il ne reçoit que du HTML déjà produit par `render()`.
  - Boucles (galerie, commentaires, miniatures) : chaque élément est rendu avec un petit
    template de fragment dans une boucle Python, les morceaux sont assemblés avec `"".join()`,
    puis injectés via `raw`.
  - Conditions (connecté ou non, message d'erreur) : décidées en Python, on passe
    un fragment rendu ou une chaîne vide.
  - Layout commun (header / main / footer) : un template `layout.html` dans lequel
    le contenu de chaque page est injecté via `raw`.
  - Pourquoi l'échappement doit être automatique : avec un échappement *opt-in* (f-strings,
    concaténation, `string.Template` utilisé directement), chaque variable oubliée dans un template
    est une faille XSS. En l'appliquant d'office dans `render()`, oublier devient impossible :
    le HTML non échappé n'entre que par `raw`, qui est visible et grep-able.
  - **À mettre en place avant d'écrire le premier template** : la rattraper après coup
    impose de repasser sur tous les fichiers de vues.
  - Pièges :
    - `$` est le caractère spécial de `string.Template` : un `$` littéral s'écrit `$$`
      → garder le CSS et le JS dans des fichiers de `static/` (les template literals JS `${...}` entrent en collision).
    - Utiliser `substitute()`, qui lève `KeyError` sur une variable manquante (les fautes de frappe
      se voient), et non `safe_substitute()`, qui les laisse passer en silence.
    - Toujours entourer les valeurs d'attributs de guillemets doubles : `value="$username"`.
    - L'échappement HTML ne suffit pas dans un attribut `href`/`src` (`javascript:...`) ni à
      l'intérieur d'une balise `<script>` → à creuser à l'étape 5.
- **Notions** : `wsgiref` et le contrat WSGI (`environ` / `start_response`), parsing de
  requêtes HTTP, `string.Template`, `html.escape`, front controller, contextes d'échappement

### Ordre conseillé à l'intérieur de l'étape 2

1. **Servir `static/`** — CSS et JS renvoyés tels quels *(attention au path traversal)*
2. **L'objet requête** : `environ` → méthode, chemin, paramètres, formulaire, cookies
3. **Le routeur** : table `(méthode, motif) → handler`, avec paramètres d'URL (`/images/<id>`)
4. **`render()`** et ses fragments
5. **Les réponses** : redirections, codes d'erreur, en-têtes
6. **Brancher les maquettes de l'étape 1.5** (~1 h) :
   - découper `layout.html` du contenu de chaque page
   - remplacer les valeurs en dur par des `$variables`
   - remplacer les liens `connexion.html` par les URL réelles `/login`
   - une route par page, qui rend son template avec des données toujours écrites en dur

   ✅ *Réussi quand* le site de l'étape 1.5 est servi par ton serveur, aux vraies URL.

## Étape 3 — Authentification

**Estimation : 8–12 h** — ✅ terminée — la plus grosse étape fonctionnelle du projet
- Inscription (email, username, mdp avec complexité minimale)
- Hash de mot de passe : `hashlib.pbkdf2_hmac('sha256', ...)`, sel aléatoire par utilisateur
  (`secrets.token_bytes`), nombre d'itérations élevé (recommandation OWASP : 600 000),
  comparaison avec `hmac.compare_digest`
  - « Maison » = assembler ces primitives, pas inventer un algorithme : un `sha256(sel + mdp)` est un
    choix faible, facile à attaquer en soutenance
- ✅ **`generate_token()` écrit dans `lib/security.py`** — une ligne, `secrets.token_urlsafe(32)`,
  mais **trois usages** :
  - le jeton de confirmation de compte *(étape 3)*
  - l'identifiant de session posé dans le cookie *(étape 3)*
  - le jeton de réinitialisation du mot de passe *(étape 4)*
  - ⚠️ `secrets`, jamais `random` : ce dernier produit des valeurs prévisibles à partir de
    quelques observations, donc des sessions devinables.
- Confirmation de compte par email (lien unique)
  - **Login refusé tant que le compte n'est pas confirmé**
- Liens dans les mails construits depuis une variable `APP_URL` (`.env`), **jamais** depuis l'en-tête
  `Host` de la requête : sinon un attaquant peut faire pointer le lien vers son propre site
- Login **par username** et mot de passe (le sujet précise username, pas email)
- Cookie de session `HttpOnly` (inaccessible au JavaScript, donc à une XSS) + `SameSite=Lax`
- Logout en un clic : bouton dans le header du layout commun → présent sur **toutes** les pages
- **`.env` et volume Docker — reportés ici depuis l'étape 1**, volontairement, pour les mettre en
  place au moment où leur absence se fait sentir plutôt que par anticipation. Deux symptômes les
  déclencheront :
  - *l'envoi du mail de confirmation depuis le conteneur échoue* → `ConnectionRefusedError` sur
    `localhost:1025`, parce que Mailpit s'appelle `mailpit` dans le réseau compose. C'est ce qui
    impose `SMTP_HOST` en variable d'environnement, donc `.env` + `env_file: .env`.
  - *les comptes de test disparaissent à chaque `docker compose down`* → il manque un volume sur
    `/app/data`, sans quoi la base repart de zéro.
  - À faire alors : `.env`, `.env.example` rempli (`APP_URL`, `SMTP_HOST`, `SMTP_PORT`, `DB_PATH`),
    `env_file: .env` et `volumes:` dans le compose.
- **Notions** : `hashlib`/`secrets`/`hmac` (salage + hash lent), `smtplib`, gestion de sessions via cookies maison

## Étape 4 — Reset password + gestion du profil

**Estimation : 4–6 h** — ✅ terminée — réutilise toute la mécanique de l'étape 3
- Mail de réinitialisation avec token à expiration, **à usage unique** (invalidé après utilisation)
- Modification username / email / mot de passe
  - Même règle de complexité du mot de passe qu'à l'inscription, au reset comme à la modification
  - Unicité du username et de l'email vérifiée aussi à la modification (sinon `sqlite3.IntegrityError`
    → erreur serveur au lieu d'un message)
- Préférence de notification des commentaires : case à cocher, cochée par défaut (cf. étape 9)
- **Notions** : gestion d'expiration de token en DB

## Étape 5 — Sécurité transverse (en continu)

**Estimation : 3–5 h** — 🚧 environ 2 h 30 faites, réparties sur les étapes 3 à 8 plutôt qu'en bloc
- ✅ **Protection CSRF sur tous les formulaires** — *double submit cookie* : jeton dans un cookie
  `csrf`, recopié dans un champ caché de chacun des 9 formulaires, comparé dans `app()` sur
  **tout** POST avant le routage. Une seule vérification, aucune liste d'exceptions.
  - Le jeton de la route de capture voyagera dans l'en-tête `X-CSRF-Token`, son corps étant
    occupé par les pixels → une source supplémentaire à accepter dans `app()` *(étape 6)*
- ✅ **Validation côté serveur de tous les formulaires** (sujet : « All your forms should have correct validations »)
  — centralisée dans `services/validators.py`, partagée par l'inscription, le reset et le profil
  - Les attributs HTML5 (`required`, `type="email"`, `minlength`) ne sont qu'un confort : contournables en une requête
- ✅ **Injection SQL** : placeholders `?` dans **toutes** les requêtes, jamais de f-string ni de concaténation dans du SQL
  — audité, les 18 requêtes du projet sont paramétrées ; les seules non paramétrées sont des `PRAGMA` constants
- ✅ Échappement des sorties (anti-XSS) → déjà garanti par défaut par `render()` (étape 2) ;
  audit fait : `raw` n'apparaît que dans `page()`, sur du HTML déjà produit par `render()`. Seul contexte
  non textuel du projet, `$reset_token` dans un `action=` → traité par `urllib.parse.quote(..., safe="")`
- ⏳ **Uploads : le serveur ne reçoit que des pixels bruts** (cf. étapes 0.5 et 6) — *à faire avec la route
  de capture, étape 6*. Vérifications, dans l'ordre :
  1. session valide + token CSRF
  2. `CONTENT_LENGTH` est un entier égal à **exactement** 640 × 480 × 4 = 1 228 800,
     vérifié **avant** de lire le corps (sinon un corps de plusieurs Go sature la mémoire)
  3. lire exactement ce nombre d'octets depuis `environ["wsgi.input"]`
  4. l'identifiant du calque appartient à une liste blanche côté serveur (`{"cat": "overlays/cat.png"}`) ;
     jamais un chemin reçu du client (path traversal : `?overlay=../../etc/passwd`)
  5. nom du fichier final généré par le serveur (`secrets.token_hex(16) + ".png"`), stocké dans `data/`,
     hors de `static/`
  6. fichier servi par une route dédiée avec `Content-Type: image/png`
  - Aucun octet reçu n'est décodé ni stocké tel quel : l'image finale est toujours produite par l'encodeur maison.
    C'est l'argument à donner en soutenance.
  - Le `Content-Type` et l'extension envoyés par le client ne valent rien comme validation
- 🚧 Contrôle d'accès (chaque utilisateur n'agit que sur ses propres données)
  - ✅ *garde d'authentification* : `if request.user is None` sur les 5 handlers du profil et l'éditeur.
    Les actions du profil écrivent toutes sur `request.user["id"]`, issu du cookie de session — aucun
    identifiant de cible n'est exprimable par le client, donc rien à falsifier
  - ⏳ *contrôle de propriété* : dès qu'une route prendra sa cible dans l'URL (`/images/<id>/delete`),
    il faudra vérifier `image["user_id"] == request.user["id"]` *(étape 8)*
- **Notions** : tokens CSRF, requêtes paramétrées, échappement HTML, validation d'un corps de requête binaire, path traversal

## Étape 6 — Webcam, capture et upload

**Estimation : 6–10 h** — le gros du JavaScript du projet
- Page réservée aux utilisateurs connectés : un visiteur non connecté est **redirigé poliment**
  vers la page de login, avec un message
- **Section principale** :
  - Preview webcam
  - Liste d'images superposables sélectionnables
  - Bouton de capture inactif tant qu'aucune image n'est sélectionnée
  - Upload alternatif (si pas de webcam) : `<input type="file">` → image chargée via `URL.createObjectURL()`
    → dessinée sur le même canvas que la webcam
- **Section latérale : miniatures de toutes les photos déjà prises par l'utilisateur**
- Chemin d'envoi **unique** pour la webcam et le fichier :
  - dessin sur un `<canvas>` 640×480 → `ctx.getImageData()` → `fetch()` en POST
  - corps = les pixels bruts ; token CSRF dans un en-tête ; identifiant du calque en paramètre
  - en cas de succès, `location.reload()` : la section latérale est re-rendue par le serveur
  - utiliser `fetch()` ici ne revient pas à faire le bonus AJAX
- ✅ **Prérequis laissé de côté à l'étape 2 — fait.** `lib/request.py` ne lisait le corps que pour un
  `Content-Type` de formulaire ; les pixels bruts, en `application/octet-stream`, n'étaient accessibles
  nulle part puisque le controller reçoit `request` et pas `environ`.
  - `_read_body()` lit désormais `wsgi.input` **une seule fois**, inconditionnellement, avec le plafond
    `SIZE_MAX`, et range les octets dans `request.body`. `_parse_form()` travaille sur `self.body` et
    conserve son test de `Content-Type` : un corps binaire ne part jamais dans `parse_qs`.
  - Un seul endroit consomme le flux, qui ne se lit qu'une fois — une seconde lecture renverrait du vide.
  - Le controller pourra écrire `if len(request.body) != 1_228_800: → refuser`.
- ✅ **Calques prêts** : trois PNG 640×480 RGBA dans `static/overlays/`, décodés au démarrage par
  `lib/overlays.py`. `OVERLAY_FILES` sert de liste blanche *(cf. vérification 4 de l'étape 5)*.
- **Notions** : `navigator.mediaDevices.getUserMedia`, `ctx.drawImage` / `ctx.getImageData`,
  `URL.createObjectURL`, `fetch` avec un corps binaire

### Ordre conseillé à l'intérieur de l'étape 6

**La preview webcam d'abord**, alors même qu'elle ne débloque rien côté serveur : c'est la seule pièce
du projet dont le fonctionnement dépend de la machine. WSL2, caméra USB externe, permission du
navigateur, *secure context* — autant le vérifier en 30 minutes plutôt qu'après avoir écrit tout le
serveur. Rappel : `getUserMedia()` n'est autorisé que sur `http://localhost`, jamais sur une IP.

Le reste suit la règle inverse : **tout le serveur avant le JavaScript de capture**, pour qu'un échec
à la dernière étape soit forcément dans le navigateur.

| | Tâche | Estimation |
|---|---|---|
| 1 | **Preview webcam seule** — `<video>` + `getUserMedia()`, avec un `.catch()` qui laisse l'upload de fichier utilisable | 0,5–1 h |
| 2 | **Fusion alpha** *(= étape 7, faite ici en pratique)* — testable hors HTTP : fausse photo unie + vrai calque → `encode()` → ouvrir le PNG | 2–3 h |
| 3 | **Route de capture serveur** — `POST /images`, les 6 vérifications de l'étape 5, stockage dans `data/`, `INSERT`, plus `GET /images/<id>` en `image/png`. Testable au `curl` avec 1 228 800 octets bidon | 2–3 h |
| 4 | **JS de capture** — canvas 640×480, sélection de calque, bouton inactif tant qu'aucun calque n'est choisi, `getImageData()`, `fetch()` avec `X-CSRF-Token` | 1,5–3 h |
| 5 | **Upload de fichier** — `URL.createObjectURL()` → même canvas, même POST | 0,5–1 h |
| 6 | **Section latérale** — miniatures des photos de l'utilisateur, rendues par le serveur | 1–1,5 h |
| 7 | **Rejet poli des non connectés** + passage de test complet | 0,5 h |
| | **Total à passer** | **8–13 h** |

La ligne 2 est l'étape 7, déjà budgétée à part : sans elle, l'étape 6 proprement dite reste à **6–10 h**.
Elle est faite ici parce que la route de capture n'a rien à stocker tant que la fusion n'existe pas.

⚠️ À ne pas oublier au point 3 : `app()` ne lit le jeton CSRF que dans `request.form`. La capture ayant
un corps binaire, `request.form` sera vide et la route prendra un **403** — il faut accepter aussi
`environ.get("HTTP_X_CSRF_TOKEN", "")`. Et côté navigateur, le cookie étant `HttpOnly`, le JS ne peut pas
le lire : le jeton doit venir du HTML, via un `<meta name="csrf-token" content="$csrf_token">` dans `layout.html`.

## Étape 7 — Fusion alpha (composition serveur)

**Estimation : 2–3 h** — courte, parce que l'étape 0.5 a fait le travail.
**Réalisée pendant l'étape 6** (point 2 de son ordre) : la route de capture n'a rien à stocker tant que
la fusion n'existe pas. Le budget reste compté ici.
- Superposition photo + calque, faite côté serveur, sur deux tampons 640×480 de même taille
- Calques déjà décodés au démarrage (étape 0.5)
- L'alpha de la photo est ignoré : l'image finale est toujours opaque (alpha = 255),
  sinon un PNG transparent uploadé laisse des trous
- Résultat encodé avec l'encodeur de l'étape 0.5
- **Notions** : formule de blending alpha (`pixel_final = fond*(1-alpha) + dessus*alpha`),
  en entiers : `(dessus * a + fond * (255 - a)) // 255`

## Étape 8 — Galerie publique

**Estimation : 5–8 h**
- Liste paginée (≥5 éléments/page), triée par date
- Likes et commentaires réservés aux utilisateurs connectés
- Suppression réservée au propriétaire de l'image
- **Notions** : pagination SQL (`LIMIT`/`OFFSET`), requêtes agrégées, contrôle d'accès en écriture

## Étape 9 — Notification email sur commentaire

**Estimation : 1–2 h** — réutilise `lib/mail.py` de l'étape 3
- Envoi automatique à l'auteur de l'image
- Préférence activée par défaut, désactivable (réglage dans le profil, cf. étape 4)
- **Notions** : `smtplib`, colonne booléenne de préférence utilisateur

## Étape 10 — Responsive : finitions

**Estimation : 1–2 h** — l'essentiel du CSS a été fait à l'étape 1.5

Il ne reste ici que les ajustements qui n'étaient pas visibles sur la maquette, une fois les
pages réellement remplies :

- Vérifier chaque page à ~400 px de large et corriger ce qui déborde
- La page d'édition en une seule colonne sur mobile (la webcam au-dessus, les miniatures en dessous)
- Les listes longues : galerie à 5 images, fil de commentaires
- **Notions** : media queries CSS, flexbox

## Étape 11 — Containerisation finale

**Estimation : 2–3 h**
- docker-compose (app + Mailpit) déjà en place depuis l'étape 0
- Volumes pour persister la DB SQLite et les images uploadées
- Variables sensibles dans `.env` (ignoré par git) : vérifier qu'aucun secret n'a été commité,
  y compris dans l'historique git
- **Déploiement en une commande** (exigé par le sujet) : `git clone` dans un dossier vide → créer `.env`
  à partir de `.env.example` → `docker compose up` → l'application fonctionne sans autre manipulation
- **Notions** : Dockerfile Python, docker-compose, gestion de volumes

## Étape 12 — Tests et debug transverse

**Estimation : 5–10 h** — l'étape la plus sous-estimée de tous les projets
- Vérification manuelle de tout le parcours utilisateur
- **Zéro erreur, warning ou ligne de log dans les consoles**, serveur et navigateur (exigé par le sujet ;
  seules les erreurs liées à `getUserMedia()` sont tolérées, faute de HTTPS)
  - Serveur : surcharger `log_message()` du handler `wsgiref` pour couper les logs d'accès
  - Navigateur : ouvrir la console sur chaque page ; fournir un favicon, sinon la requête
    automatique vers `/favicon.ico` en 404 peut y apparaître
- Compatibilité Firefox ≥ 41 / Chrome ≥ 46 (exigée par le sujet, jamais vérifiée en pratique) :
  `.then()` plutôt que `async`/`await`, flexbox plutôt que CSS grid — ne pas y investir plus de temps
- Correction des bugs découverts tardivement

## Étape 13 — Bonus (uniquement si le mandatory est parfait)

**Estimation : sans objet** — uniquement si tout le reste est parfait
- Pistes possibles : AJAX, preview live sur le flux webcam, pagination infinie, partage réseaux sociaux, rendu GIF animé

---

## Estimation globale

| Étape | | Estimation |
|---|---|---|
| 0 | Setup projet | 3–5 h ✅ |
| 0.5 | Codec PNG | 5–8 h ✅ |
| 1 | Schéma de base de données | 2–3 h ✅ |
| 1.5 | Maquette HTML/CSS de tout le site | 3–4 h ✅ |
| 2 | Routing HTTP et rendu des vues | 7–11 h ✅ |
| 3 | Authentification | 8–12 h ✅ |
| 4 | Reset password + profil | 4–6 h ✅ |
| 5 | Sécurité transverse | 3–5 h 🚧 |
| 6 | Webcam, capture et upload | 6–10 h 🚧 |
| 7 | Fusion alpha | 2–3 h |
| 8 | Galerie publique | 5–8 h |
| 9 | Notification email | 1–2 h |
| 10 | Responsive : finitions | 1–2 h |
| 11 | Containerisation finale | 2–3 h |
| 12 | Tests et debug transverse | 5–10 h |
| | **Total** | **57–92 h** |
| | dont terminé — étapes 0 à 4 | 32–49 h |
| | dont déjà fait sur 5 et 6 | ≈ 3 h 30 |
| | **Restant** | **≈ 21–39 h** |

*Les 3 h 30 déjà passées sur les étapes 5 et 6 : la protection CSRF (≈ 2 h 30), puis les calques,
leur décodage au démarrage et le refactor de `request.body` (≈ 1 h).*

*L'ajout de l'étape 1.5 ne change pas le restant : l'essentiel du CSS y est simplement déplacé
depuis l'étape 10, qui passe de 3–5 h à 1–2 h.*

**Ce que ces chiffres supposent** : que les décisions techniques de ce document sont suivies
(pixels bruts, `string.Template`, framework CSS classless, taille fixe 640×480). Chacune de ces
décisions économise plusieurs heures — les reconsidérer en cours de route change l'estimation.

**Ce qui fait varier le résultat** : le débogage, pas l'écriture. Les trois grosses étapes — 2, 3
et 6 — représentent à elles seules près de la moitié du total. Ce sont elles qu'il faut attaquer
avec du temps devant soi, pas en fin de soirée.

**Ce qui n'est pas compté** : le temps d'apprentissage des notions réellement nouvelles, et les
interruptions. Sur un rythme d'étudiant, compte plutôt en semaines de calendrier qu'en heures
cumulées.

---

## Point de contrôle clé
L'étape 0.5 (codec PNG) reste le poste le plus incertain du projet.

Estimation : **5–8h**. Le choix des pixels bruts réduit le périmètre : le décodeur ne lit que les calques
du projet (RGBA 8 bits, non entrelacés, 640×480). Il n'a ni à se défendre contre des fichiers malveillants,
ni à gérer les autres variantes de PNG. `zlib` fait la compression ; le vrai travail est le défiltrage
des scanlines.

Fallback Pillow : défendable en soutenance (GD est bundled avec PHP), mais c'est un pari
sur l'interprétation du correcteur, sur la partie la plus intéressante du projet.
À n'activer que si le budget 8h est franchement dépassé.
