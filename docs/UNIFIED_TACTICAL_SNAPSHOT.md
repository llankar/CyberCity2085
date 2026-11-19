# Contrat de reprise tactique — protocole 2, instantané 1

La campagne reste exclusivement écrite par Python. Godot écrit `tactical_snapshot.json` dans le répertoire UUID de sa session. Cette écriture ne distribue aucun fonds, XP, objet ou conséquence de campagne.

## Périmètre de l’instantané

- Identités de session/mission, version et empreinte du handoff (carte, déploiement et données tactiques ; audio et transport exclus de cette empreinte).
- Dictionnaires réels des agents, soutiens, ennemis et véhicules décoratifs : position, PV, PA, statistiques, effets et actions.
- Tours, camp actif, délai de la phase ennemie, sélection, confirmation de fin de tour, postures et journal.
- Objectif, progression et état d’accomplissement.
- Caméra et viewport de référence, projection, mode graphique, orientations enregistrées et bookmark musical lorsqu’il existe. À résolution identique, la caméra reprend sa position ; si la résolution a changé, le cadrage de l’escouade est recalculé pour le nouveau viewport.

Les murs, collisions, couvertures statiques, textures, règles et données de campagne **ne sont pas importés de l’instantané**. Ils sont chargés depuis le même handoff et les sources existantes. Les réglages globaux de qualité restent ceux du joueur.

## Frontière de cohérence

`_sync_display()` programme une écriture différée, regroupée en fin de frame. La logique d’action et la boucle IA sont synchrones : l’écriture arrive après leur retour, pas au milieu d’une série de dégâts. Un fichier temporaire remplace atomiquement le dernier état complet. En cas d’arrêt pendant une action, la reprise revient au dernier état logique enregistré ; les animations/particules en cours ne sont pas rejouées.

La caméra et les orientations enregistrées sont restaurées. Les futurs tirages du RNG global Godot ne sont pas sérialisés : aucune identité des jets futurs après redémarrage n’est promise. Les probabilités et calculs de combat restent inchangés.

## Reprise explicite et isolation

1. CONTINUE charge le checkpoint Python et propose REPRENDRE [S] si un instantané existe et qu’aucun résultat n’attend confirmation.
2. Python valide entièrement le JSON, les nombres finis, identités, bornes, déploiement, PV, PA, positions et empreinte.
3. Une nouvelle session UUID reçoit une copie de l’état tactique avant même le lancement du processus. Si le lancement échoue, l’ancienne session redevient récupérable. Si le nouveau processus échoue avant sa première frame, sa copie permet une nouvelle reprise.
4. Godot valide à nouveau avant de restaurer. Les positions ne sont pas replacées par le générateur de rencontre. Données invalides : message d’erreur, aucun combat neuf lancé silencieusement.
5. Une commande locale identifiée clôt l’ancienne instance. Ses fichiers restent isolés et ses résultats ne peuvent plus modifier la campagne.
6. Un résultat préparé/confirmé impose sa récupération explicite ; S ne permet pas de l’effacer en reprenant un état antérieur.
7. Si la campagne est déjà résolue, la reprise renvoie l’ACK depuis le résultat validé et présente les écrans restants, sans résoudre une deuxième fois.

Les anciennes sessions sans ces nouveaux canaux restent lisibles et disposent du parcours de secours explicite. Aucun PID lu dans une sauvegarde n’est tué pour rechercher une ancienne instance.
