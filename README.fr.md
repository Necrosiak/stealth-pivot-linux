# Turtle Beach Stealth Pivot sous Linux

[Documentation complète en anglais](README.md)

Ce correctif permet au **récepteur USB 2,4 GHz `10f5:7101`** d’utiliser le pilote Linux `xpad` déjà fourni par la distribution. Il ne compile aucun pilote et ne modifie pas le firmware.

## Installation

Sur une distribution avec systemd, udev, Bash, kmod, util-linux et le module `xpad` :

```bash
git clone https://github.com/Necrosiak/stealth-pivot-linux.git
cd stealth-pivot-linux
sudo bash install.sh
```

Allumer et associer la manette au récepteur. Steam peut l’afficher sous **Generic X-Box pad**.

```bash
bash status.sh
```

Le service réapplique le réglage au démarrage et au branchement du récepteur. Les fichiers sont conservés dans `/etc`, et le pilote utilisé est celui du noyau courant. L’état `inactive (dead)` est normal après une exécution réussie.

## Mise à jour et suppression

```bash
git pull --ff-only
sudo bash install.sh
```

```bash
sudo bash uninstall.sh
```

La désinstallation restaure la configuration présente avant la première installation. Les sauvegardes restent dans `/var/lib/stealth-pivot-linux/original`. Un redémarrage efface l’enregistrement en mémoire ; un ancien contournement restauré peut le réappliquer.

## Ce qui est vérifié

Sur Bazzite 44 avec le noyau `7.2.11-ogc4.1.fc44.x86_64`, l’enregistrement du récepteur a créé une manette reconnue par Linux et Steam. Son interface HID séparée reste intacte.

**Le redémarrage, le débranchement/rebranchement, une mise à jour du système et le test complet des touches/vibrations restent à confirmer pour cette version du dépôt.** Les autres distributions systemd sont des candidates, pas des configurations matériellement validées. Le Bluetooth et le branchement filaire direct ne sont pas couverts.

Ce contournement n’est pas une intégration officielle au noyau. Un futur changement incompatible de `xpad` peut demander une adaptation. Voir le README anglais pour les détails et les journaux à fournir.
