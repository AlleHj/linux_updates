# Linux Updates for Home Assistant

![Version](https://img.shields.io/badge/version-1.7.0-blue.svg)
![Home Assistant](https://img.shields.io/badge/home%20assistant-component-orange.svg)

En kraftfull Custom Component för Home Assistant som övervakar och hanterar paketuppdateringar på dina Linux-servrar (Ubuntu/Debian) via SSH.

Integrationen kräver ingen agent eller installation på servern, endast SSH-åtkomst.

## Funktioner

* **Övervakning:** Visar antal tillgängliga uppdateringar (inklusive `held back` paket som kernels).
* **Paketlista:** Se vilka paket som väntar på uppdatering direkt i Home Assistant attributen.
* **Åtgärder:**
    * **Run Updates:** Utför `apt-get update`, `dist-upgrade` och `autoremove` med ett knapptryck.
    * **Reboot:** Starta om servern direkt från HA.
    * **Check Updates:** Manuell kontroll av uppdateringar utan att vänta på schemat.
* **Status:** Sensorer för när senaste kontrollen och senaste uppdateringen lyckades.
* **Felhantering:** "Update Problem"-sensor som larmar om SSH-kopplingen bryts eller uppdateringen misslyckas.
* **Konfigurerbar:** Ställ in hur ofta integrationen ska söka efter uppdateringar (standard: 6 timmar).

## Installation

### Alternativ 1: Manuell Installation
1.  Ladda ner mappen `linux_updates` från detta repository.
2.  Kopiera mappen till `custom_components/` i din Home Assistant-konfiguration.
3.  Starta om Home Assistant.

### Konfiguration
1.  Gå till **Inställningar** -> **Enheter & Tjänster**.
2.  Klicka på **Lägg till Integration** och sök efter "Linux Updates".
3.  Fyll i uppgifterna:
    * **Host:** IP-adress till din Linux-server.
    * **Username:** SSH-användarnamn.
    * **Password:** Lösenord (eller lämna tomt om du använder nyckel).
    * **SSH Key File:** Sökväg till din privata SSH-nyckel (valfritt, t.ex. `/config/ssh_keys/id_rsa`).
    * **Scan Interval:** Hur ofta (i timmar) systemet ska söka efter uppdateringar.

### Sudo-rättigheter (Viktigt)
För att knapparna **Run Updates** och **Reboot** ska fungera utan att fastna vid lösenordsfrågor, bör användaren ha `NOPASSWD` rättigheter för `apt-get` och `reboot` i `/etc/sudoers` på servern:

```bash
# Kör 'sudo visudo' på linux-servern och lägg till:
anvandarnamn ALL=(ALL) NOPASSWD: /usr/bin/apt-get, /usr/sbin/reboot