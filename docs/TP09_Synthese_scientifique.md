# TP09 — Synthèse scientifique globale

## 1. Analyse de la latence — TP06

L'étude du temps aller-retour (RTT) a été réalisée
à partir des échanges CoAP entre cinq clients et
un serveur dans une topologie multi-sauts.

Nombre de transmissions observées : 13334.
Messages reçus par le serveur : 13333.
Réponses reçues par les clients : 13333.
RTT moyen des réponses : 146.11 ms.

Une transmission reste sans réponse observée à
la fin de la capture. Elle est considérée comme
incomplète et non comme une perte confirmée.

## 2. Analyse de la scalabilité — TP07

L'étude de scalabilité compare trois configurations :
5, 10 et 20 clients.

RTT moyen pour 5 clients : 143.67 ms.
RTT moyen pour 10 clients : 176.41 ms.
RTT moyen pour 20 clients : 193.84 ms.

Entre 5 et 20 clients, le RTT moyen augmente de
34.92 %.

Le PDR observé reste égal à 100 % dans les neuf
simulations étudiées. La croissance du réseau
s'accompagne donc d'une augmentation du délai
sans perte applicative observée dans ces conditions.

## 3. Comparaison CoAP CON / NON — TP08

Trois conditions radio ont été évaluées :

Q1 : RX ratio = 100 %.
Q2 : RX ratio = 90 %.
Q3 : RX ratio = 50 %.

Chaque condition a été testée avec trois seeds.

En Q1 et Q2, CON et NON atteignent un PDR de 100 %.

En Q3, le PDR moyen de CON est de
95.86 %,
contre 90.38 % pour NON.

La différence observée est de
5.48 points de pourcentage.

Le RTT moyen des réponses reçues en mode CON
atteint 211.60 ms en Q3.

## 4. Limites expérimentales

- Les résultats sont issus de simulations Cooja.
- Trois répétitions par scénario ne permettent
  pas une généralisation statistique forte.
- Les nombres de messages envoyés diffèrent
  entre CON et NON en Q3.
- Le RTT du mode NON n'a pas été mesuré.
- Les retransmissions internes CoAP et MAC
  n'ont pas été comptabilisées séparément.
- Le nombre de sauts RPL réel n'a pas été
  confirmé par une analyse des routes.

## 5. Conclusion générale

Les simulations montrent que le protocole CoAP,
associé à RPL et 6LoWPAN, permet des échanges
applicatifs fiables dans les conditions étudiées.

L'augmentation du nombre de clients entraîne une
hausse du RTT moyen. La dégradation importante
des conditions radio réduit le taux de livraison
et augmente le RTT des réponses CON reçues.

Dans le scénario fortement dégradé, le mode CON
présente un PDR moyen supérieur au mode NON.
Cependant, cette observation doit être interprétée
avec prudence en raison de la différence de trafic
et du nombre limité de répétitions.
