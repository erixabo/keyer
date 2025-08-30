# iambic_keyer

Egyszerű **iambic A** CW keyer Pythonban, amely az **egér bal és jobb gombját** használja paddle-ként.  
- **Bal gomb (BTN_LEFT)** → DIT (`·`)  
- **Jobb gomb (BTN_RIGHT)** → DAH (`–`)  
- **Mindkettő együtt** → iambic squeeze (váltakozó pont–vonal).  

A kimenet hang formájában (sidetone) jelenik meg a hangkártyán keresztül.

---

## Funkciók
- CW jel generálás **valós WPM alapján** (PARIS standard szerint).  
- Folyamatos pont/vonás sorozat a gomb tartása alatt.  
- Iambic A mód támogatás (felváltva adja a pontot és vonást, ha mindkettő lenyomva van).  
- Rámpás hangindítás/leállítás → nincs kattanás.  
- Egyszerű, hordozható Python kód.  

---

## Követelmények
- Linux (X11/Wayland alatt is működik).  
- Python 3.8+  
- Telepített csomagok:
  ```bash
  pip install evdev sounddevice numpy
  ```

### Jogosultság
Az `/dev/input/eventX` eszközökhöz hozzáférés kell.  
Tedd magad az `input` csoportba:
```bash
sudo usermod -aG input $USER
```
Ezután **logout/login** vagy reboot.  
Ellenőrizheted:
```bash
id
```
→ a `groups` listában ott kell legyen az `input`.

---

## Használat
1. Derítsd ki, melyik `eventX` az egér:
   ```bash
   grep -B5 -A5 -i mouse /proc/bus/input/devices
   ```
   Példa kimenet:
   ```
   N: Name="PixArt Lenovo USB Optical Mouse"
   H: Handlers=mouse0 event3
   ```
   → itt az `event3` kell.

2. Állítsd be a kódban:
   ```python
   MOUSE_EVENT = "/dev/input/event3"
   ```

3. Indítsd:
   ```bash
   python iambic_keyer.py
   ```

---

## Billentyűk és viselkedés
- **BAL egérgomb**: `titititi…` (folyamatos DIT sorozat).  
- **JOBB egérgomb**: `tátátá…` (folyamatos DAH sorozat).  
- **Mindkettő**: `titatita…` (iambic squeeze).  
- **Ctrl+C**: kilépés.  

Alapértelmezett sebesség: **20 WPM**, állítható a kódban.  

---

## Tervek
- Futás közbeni WPM állítás (`[` = lassabb, `]` = gyorsabb).  
- Terminálban `.` és `–` karakterek megjelenítése a jelekhez.  
- Kimenet GPIO-ra / soros portra → rádió kulcsoláshoz.  
- Iambic B mód támogatása.  

---

## Licenc
MIT License – © 2025 Szabó Erik  
Lásd a [LICENSE](LICENSE) fájlt a részletekért.
