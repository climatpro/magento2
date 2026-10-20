# Climapro - Devis signes a planifier

| | |
|---|---|
| ID n8n | `41rkj8mIgjXlAuat` |
| Actif | oui |
| Déclencheur | cron toutes les 30 min (node "Toutes les 30 min"), timezone Europe/Paris |
| Export | `workflows/climapro-devis-signes-a-planifier.json` |

## Rôle
Toutes les 30 min, lit les devis signés Interfast (filtre natif `toPlan=true`), retire ceux déjà pris en charge (intervention portant le n° de devis, intervention chez le même client depuis la signature, ou devis facturé à plus de 80 %) et maintient la table `devis_a_planifier` lue par le tableau de bord.
Affecte un responsable (Christophe / Laurent) par regex sur le titre du devis. Lecture seule Interfast, aucune IA.

## Services appelés
- Interfast (GET /v1/billing/quotations `toPlan=true`, page 0, size 100, `orderBy=signedAt` ; GET /v1/events, 15 pages × 100, de −8 mois à +13 mois) — direct via HTTP Request, credential "Interfast API" (`GgJ5wsyGIUSWY0cN`)
- Data Tables n8n : `devis_a_planifier` (`0U759buKi8psn4V5`) — lecture complète (node "Lire table") et upsert sur `reference` (node "Enregistrer")

## Modèle IA
Aucun.

## Sous-workflows appelés
aucun

## Appelé par
Aucun autre workflow exporté ne l'appelle (déclencheur autonome, ou appel externe : Claude, iPhone, navigateur).

## Points fragiles
- Une seule page de devis (`size=100`) : au-delà de 100 devis signés à planifier, les plus anciens sont ignorés.
- Pagination des interventions limitée à 15 × 100 = 1 500 événements sur 21 mois ; `onError: continueRegularOutput` : si Interfast events échoue, `parRef`/`parClient` sont vides et **tous** les devis réapparaissent comme non planifiés (et les lignes `mail` ne sont pas fermées).
- Date pivot `DEPUIS = '2026-01-01'` en dur (devis signés avant ignorés) ; comparaison de dates en chaînes.
- Heuristique « une intervention chez le même client après la signature = devis pris en charge » : peut masquer un devis réellement non planifié chez un client multi-chantiers.
- Seuil « facturé à plus de 80 % » (`balance <= 0.2 × amountVAT`) en dur.
- Regex de répartition CHRISTOPHE / LAURENT dupliquées avec "Climapro - Devis acceptes par mail" (2 copies là-bas) ; défaut = Christophe.
- `saveDataSuccessExecution: none` : aucune trace des exécutions réussies pour diagnostiquer a posteriori.
- Couplage implicite avec "Devis acceptes par mail" via le champ `source` de la table : les deux workflows écrivent la même table avec des règles de fermeture différentes.
