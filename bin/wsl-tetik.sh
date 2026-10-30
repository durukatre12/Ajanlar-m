#!/usr/bin/env bash
# Windows Görev Zamanlayıcı → WSL köprüsü. `bin/zamanla_windows.py` kurduğu görevler bunu çağırır.
# Kullanım: bin/wsl-tetik.sh sabah | saatlik | aksam | servis
#   sabah   → gunluk.py --sabah   (günün planı kuyruğa + dağıtıcı + sabah raporu)
#   saatlik → dagitici.py         (sırada bekleyen işleri alır)
#   aksam   → gunluk.py --aksam   (günün denetimi)
#   servis  → köy (bin/koy.py) arka planda + Telegram dinleyici önde; oturum açıkken hep çalışır
set -uo pipefail
KOK="$(cd "$(dirname "$0")/.." && pwd)"
cd "$KOK" || exit 1
mkdir -p sirket-log

# Görev Zamanlayıcı'nın açtığı kabuk etkileşimsizdir; `claude`'un kurulduğu yerleri PATH'e ekle.
export PATH="$HOME/.local/bin:$HOME/.npm-global/bin:$HOME/.claude/local:$HOME/bin:/usr/local/bin:$PATH"
if [ -s "$HOME/.nvm/nvm.sh" ]; then . "$HOME/.nvm/nvm.sh" >/dev/null 2>&1; fi

LOG="sirket-log/zamanlayici.log"
damga() { date "+%Y-%m-%dT%H:%M:%S%z"; }

case "${1-}" in
  sabah)   echo "$(damga) | sabah" >>"$LOG";   python3 bin/gunluk.py --sabah >>"$LOG" 2>&1 ;;
  saatlik) echo "$(damga) | saatlik" >>"$LOG"; python3 bin/dagitici.py   >>"$LOG" 2>&1 ;;
  aksam)   echo "$(damga) | aksam" >>"$LOG";   python3 bin/gunluk.py --aksam >>"$LOG" 2>&1 ;;
  servis)
    echo "$(damga) | servis açıldı" >>"$LOG"
    pkill -f "bin/koy.py" 2>/dev/null; pkill -f "bin/telegram_dinle.py" 2>/dev/null
    nohup python3 bin/koy.py >>sirket-log/koy.log 2>&1 &
    exec python3 bin/telegram_dinle.py >>sirket-log/telegram-dinle.log 2>&1
    ;;
  *) echo "kullanım: bin/wsl-tetik.sh sabah|saatlik|aksam|servis" >&2; exit 2 ;;
esac
