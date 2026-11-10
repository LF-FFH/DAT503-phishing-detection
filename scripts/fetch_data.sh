#!/usr/bin/env bash
# Lädt die beiden öffentlichen Datensätze in einer FESTEN Version (Commit-Hash) nach data/raw/.
# Die Rohdaten werden nicht ins Repo eingecheckt (Größe ~2,5 GB, Lizenz CC BY-NC 4.0 bzw. GPL).
set -euo pipefail
mkdir -p data/raw
fetch() {  # $1 = URL, $2 = Zielordner, $3 = Commit
  if [ -d "$2/.git" ]; then echo "$2 existiert bereits – übersprungen"; return; fi
  git init -q "$2"
  git -C "$2" remote add origin "$1"
  git -C "$2" fetch -q --depth 1 origin "$3"
  git -C "$2" checkout -q FETCH_HEAD
  echo "$2 @ $(git -C "$2" rev-parse --short HEAD)"
}
fetch https://github.com/rf-peixoto/phishing_pot      data/raw/phishing_pot     78be141545ed9e56eefb857808ac78e83eb81b81
fetch https://github.com/MWiechmann/enron_spam_data  data/raw/enron_spam_data  e73c300263040f84b954e969ac06821c31cff47a
