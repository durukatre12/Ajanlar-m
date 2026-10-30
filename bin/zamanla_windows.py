#!/usr/bin/env python3
"""Zamanlayıcı kurucusu — Windows (WSL içinden). Windows Görev Zamanlayıcı'ya dört görev yazar.

  sabah    09:00                 → `bin/wsl-tetik.sh sabah`   günün planı + dağıtıcı + sabah raporu
  saatlik  10:05–22:05, saatte 1 → `bin/wsl-tetik.sh saatlik` sırada bekleyen işleri alır
  aksam    22:00                 → `bin/wsl-tetik.sh aksam`   günün denetimi
  servis   oturum açılınca       → `bin/wsl-tetik.sh servis`  köy (localhost:8765) + Telegram dinleyici

Neden WSL içinden Windows görevi: WSL'de cron, WSL kapalıyken çalışmaz. Görev Zamanlayıcı ise
saat gelince WSL'i kendisi açar; bilgisayar o saatte uykudaysa açılınca kaçan görevi koşturur
(StartWhenAvailable). Görevler `conhost --headless` ile açılır — ekranda pencere belirmez.

Kullanım (WSL terminalinde, repo kökünde):
  python3 bin/zamanla_windows.py --kuru     # kurulacak görevleri ve XML'i bas, hiçbir şeye dokunma
  python3 bin/zamanla_windows.py --kur      # görevleri yaz (schtasks.exe)
  python3 bin/zamanla_windows.py --durum    # görevler kayıtlı mı, sonraki çalışma ne zaman
  python3 bin/zamanla_windows.py --kaldir   # görevleri sil (rapor dosyalarına dokunmaz)
  python3 bin/zamanla_windows.py --simdi servis   # bir görevi hemen başlat (ör. köyü şimdi aç)
"""
import os
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from xml.sax.saxutils import escape

sys.path.insert(0, str(Path(__file__).resolve().parent))
import ayar  # noqa: E402

KOK = ayar.KOK
KLASOR = "\\AjanKoyu\\"

GOREVLER = [
    {"ad": "sabah", "tetik": "takvim", "saat": f"{ayar.MESAI_BASLANGIC:02d}:00", "ne": "günün planı + dağıtıcı"},
    {"ad": "saatlik", "tetik": "takvim", "saat": f"{ayar.MESAI_BASLANGIC + 1:02d}:05",
     "tekrar": "PT1H", "sure": f"PT{ayar.MESAI_BITIS - ayar.MESAI_BASLANGIC - 1}H", "ne": "sıradaki işler"},
    {"ad": "aksam", "tetik": "takvim", "saat": f"{ayar.MESAI_BITIS - 1:02d}:00", "ne": "günün denetimi"},
    {"ad": "servis", "tetik": "oturum", "ne": "köy + Telegram dinleyici"},
]


def wsl_mi():
    try:
        return "microsoft" in Path("/proc/version").read_text(encoding="utf-8").lower()
    except OSError:
        return False


def dagitim_adi():
    return os.environ.get("WSL_DISTRO_NAME") or "Ubuntu"


def windows_kullanicisi():
    """`BILGISAYAR\\kullanici` — görevler bu hesaba bağlanır. Oturum tetiği kullanıcısız olursa
    Windows onu "herkes için" sayar ve yönetici izni ister ("Erişim engellendi")."""
    try:
        cikti = subprocess.run(["whoami.exe"], capture_output=True, timeout=15).stdout
    except (OSError, subprocess.SubprocessError):
        return ""
    return cikti.decode("utf-8", errors="replace").strip()


def _windows_yolu(yol):
    """WSL yolunu Windows yoluna çevirir (wslpath -w)."""
    return subprocess.run(["wslpath", "-w", str(yol)], capture_output=True, text=True,
                          check=True).stdout.strip()


def komut_argumanlari(gorev):
    """Görevin Windows tarafında çalıştıracağı komut: conhost --headless wsl.exe -d <dağıtım> -- <betik> <ad>."""
    betik = KOK / "bin" / "wsl-tetik.sh"
    return f"--headless wsl.exe -d {dagitim_adi()} -- {betik} {gorev['ad']}"


def gorev_xml(gorev, simdi=None, kullanici=""):
    """Görev Zamanlayıcı XML'i (UTF-16 ile yazılır). StartWhenAvailable açık, aynı anda tek örnek.
    `kullanici` verilirse görev ve oturum tetiği o hesaba bağlanır (yönetici izni gerekmez)."""
    tarih = (simdi or datetime.now()).strftime("%Y-%m-%d")
    kim = f"<UserId>{escape(kullanici)}</UserId>" if kullanici else ""
    if gorev["tetik"] == "oturum":
        tetik = f"<LogonTrigger><Enabled>true</Enabled>{kim}</LogonTrigger>"
        sinir = "PT0S"   # servis süresiz çalışır
    else:
        tekrar = ""
        if gorev.get("tekrar"):
            tekrar = (f"<Repetition><Interval>{gorev['tekrar']}</Interval>"
                      f"<Duration>{gorev['sure']}</Duration><StopAtDurationEnd>false</StopAtDurationEnd></Repetition>")
        tetik = (f"<CalendarTrigger>{tekrar}<StartBoundary>{tarih}T{gorev['saat']}:00</StartBoundary>"
                 f"<Enabled>true</Enabled><ScheduleByDay><DaysInterval>1</DaysInterval></ScheduleByDay>"
                 f"</CalendarTrigger>")
        sinir = "PT2H"
    return f"""<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.4" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <RegistrationInfo><Description>Ajan Köyü — {escape(gorev['ne'])}</Description></RegistrationInfo>
  <Triggers>{tetik}</Triggers>
  <Principals><Principal id="Author">{kim}<LogonType>InteractiveToken</LogonType><RunLevel>LeastPrivilege</RunLevel></Principal></Principals>
  <Settings>
    <MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>
    <DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries>
    <StopIfGoingOnBatteries>false</StopIfGoingOnBatteries>
    <StartWhenAvailable>true</StartWhenAvailable>
    <RunOnlyIfNetworkAvailable>false</RunOnlyIfNetworkAvailable>
    <ExecutionTimeLimit>{sinir}</ExecutionTimeLimit>
    <Enabled>true</Enabled>
  </Settings>
  <Actions Context="Author">
    <Exec><Command>conhost.exe</Command><Arguments>{escape(komut_argumanlari(gorev))}</Arguments></Exec>
  </Actions>
</Task>
"""


def _schtasks(*argv):
    try:
        sonuc = subprocess.run(["schtasks.exe", *argv], capture_output=True, timeout=30)
    except (OSError, subprocess.SubprocessError) as exc:
        return 1, f"schtasks.exe çağrılamadı: {type(exc).__name__}"
    cikti = (sonuc.stdout + sonuc.stderr).decode("utf-8", errors="replace").strip()
    return sonuc.returncode, cikti


def tam_ad(gorev):
    return f"{KLASOR}{gorev['ad']}"


def kur():
    os.chmod(KOK / "bin" / "wsl-tetik.sh", 0o755)
    (KOK / "sirket-log").mkdir(exist_ok=True)
    kullanici = windows_kullanicisi()
    sonuclar = []
    for gorev in GOREVLER:
        with tempfile.NamedTemporaryFile("wb", suffix=".xml", delete=False, dir=KOK / "sirket-log") as dosya:
            dosya.write(gorev_xml(gorev, kullanici=kullanici).encode("utf-16"))
            yol = Path(dosya.name)
        kod, cikti = _schtasks("/Create", "/F", "/TN", tam_ad(gorev), "/XML", _windows_yolu(yol))
        yol.unlink(missing_ok=True)
        sonuclar.append((gorev["ad"], "kuruldu" if kod == 0 else f"kurulamadı: {cikti}"))
    return sonuclar


def kaldir():
    return [(g["ad"], "silindi" if _schtasks("/Delete", "/F", "/TN", tam_ad(g))[0] == 0 else "zaten yoktu")
            for g in GOREVLER]


def main(argv):
    if "--kuru" in argv:
        for gorev in GOREVLER:
            print(f"--- {tam_ad(gorev)} · {gorev.get('saat', 'oturum açılınca')} · {gorev['ne']}")
            print(f"    conhost.exe {komut_argumanlari(gorev)}")
        print("\n--- örnek XML (saatlik) ---")
        print(gorev_xml(GOREVLER[1]))
        print("(kuru koşu: hiçbir görev yazılmadı)")
        return 0
    if not wsl_mi():
        print("Bu betik Windows'ta WSL içinden çalışır. macOS: bin/zamanla.py · Linux: docs/02-dongu.md (cron).",
              file=sys.stderr)
        return 1
    if "--kur" in argv:
        for ad, mesaj in kur():
            print(f"{ad:<8} {mesaj}")
        print("\nKöyü ve dinleyiciyi şimdi açmak için: python3 bin/zamanla_windows.py --simdi servis")
        return 0
    if "--kaldir" in argv:
        for ad, mesaj in kaldir():
            print(f"{ad:<8} {mesaj}")
        return 0
    if "--durum" in argv:
        for gorev in GOREVLER:
            kod, cikti = _schtasks("/Query", "/TN", tam_ad(gorev), "/FO", "LIST")
            print(f"--- {tam_ad(gorev)}\n{cikti if kod == 0 else 'kurulu değil'}")
        return 0
    if "--simdi" in argv:
        ad = argv[argv.index("--simdi") + 1] if len(argv) > argv.index("--simdi") + 1 else ""
        gorev = next((g for g in GOREVLER if g["ad"] == ad), None)
        if not gorev:
            print("hangi görev? sabah | saatlik | aksam | servis", file=sys.stderr)
            return 2
        kod, cikti = _schtasks("/Run", "/TN", tam_ad(gorev))
        print(cikti)
        return 0 if kod == 0 else 1
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
