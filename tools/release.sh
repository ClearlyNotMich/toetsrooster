#!/usr/bin/env bash
# Publiceert een release van HEAD: tools/release.sh vX.Y.Z notes.md
set -euo pipefail
versie=${1:?gebruik: tools/release.sh vX.Y.Z NOTES_FILE}
notes=$(realpath "${2:?gebruik: tools/release.sh vX.Y.Z NOTES_FILE}")
repo=ClearlyNotMich/toetsrooster
cd "$(git rev-parse --show-toplevel)"

[ -z "$(git status --porcelain)" ] || { echo "Werkmap is niet schoon." >&2; exit 1; }
git fetch -q origin main
sha=$(git rev-parse HEAD)
[ "$sha" = "$(git rev-parse origin/main)" ] || { echo "HEAD is niet gelijk aan origin/main." >&2; exit 1; }
! gh release view "$versie" -R "$repo" >/dev/null 2>&1 || { echo "Release $versie bestaat al." >&2; exit 1; }
! git ls-remote --exit-code --tags origin "refs/tags/$versie" >/dev/null || { echo "Tag $versie bestaat al." >&2; exit 1; }

run=""
for _ in $(seq 60); do
  run=$(gh run list -R "$repo" --commit "$sha" --branch main --limit 1 --json databaseId -q '.[0].databaseId')
  [ -n "$run" ] && break
  sleep 10
done
[ -n "$run" ] || { echo "Geen CI-run voor $sha gevonden." >&2; exit 1; }
gh run watch "$run" -R "$repo" --exit-status >/dev/null
[ "$(gh run view "$run" -R "$repo" --json headSha -q .headSha)" = "$sha" ]

tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
gh run download "$run" -R "$repo" -D "$tmp/art"
cd "$tmp"
mv art/OWB-Toetsrooster-Windows/OWB-Toetsrooster.exe OWB-Toetsrooster.exe
mv art/OWB-Toetsrooster-Linux/OWB-Toetsrooster OWB-Toetsrooster-linux
chmod +x OWB-Toetsrooster-linux
git -C "$OLDPWD" show "$sha:OWB Exam Roster Generator.txt" > OWB-Exam-Roster-Generator.txt
git -C "$OLDPWD" show "$sha:OWB Retake Exam Roster Generator.txt" > OWB-Retake-Exam-Roster-Generator.txt
git -C "$OLDPWD" show "$sha:voorbeeld/Voorbeeld rooster.xlsx" > Voorbeeld-rooster.xlsx
assets=(OWB-Toetsrooster.exe OWB-Toetsrooster-linux OWB-Exam-Roster-Generator.txt OWB-Retake-Exam-Roster-Generator.txt Voorbeeld-rooster.xlsx)
sha256sum "${assets[@]}" > SHA256SUMS.txt

mkdir zelftest
QT_QPA_PLATFORM=offscreen ./OWB-Toetsrooster-linux --controle Voorbeeld-rooster.xlsx zelftest
sha256sum -c SHA256SUMS.txt

gh release create "$versie" -R "$repo" --target "$sha" --title "Toetsrooster $versie" --notes-file "$notes" "${assets[@]}" SHA256SUMS.txt
gh release view "$versie" -R "$repo" --json isDraft,targetCommitish,assets -q '"draft: \(.isDraft), doel: \(.targetCommitish)", (.assets[] | "\(.name) \(.size)")'
