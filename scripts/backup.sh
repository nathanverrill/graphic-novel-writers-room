#!/usr/bin/env bash
# Copies what git does not hold to the private backup bucket, encrypted with gpg.
#
#   scripts/backup.sh mac            this Mac: untracked and git-ignored files in the repo
#   scripts/backup.sh vm             the VM: the same, plus /home/nathan/backups and the SeaweedFS volume
#   scripts/backup.sh mac --dry-run  list what would be sent, send nothing
#
# The passphrase lives in a local file (BACKUP_KEY), never in git. Keep a copy in a password manager:
# without it the archives cannot be opened.
# Restore into a new folder, never over live files:
#   gcloud storage cp <object> - | gpg --batch --decrypt --passphrase-file KEY | tar -x -C NEW_DIR
set -euo pipefail

WHERE=${1:?usage: backup.sh mac|vm [--dry-run]}
DRY=${2:-}
BUCKET=${BACKUP_BUCKET:-gs://writers-room-backups-voltaic-quest-502915-u7}
KEY=${BACKUP_KEY:-$HOME/.config/writers-room-backup/key}
STAMP=$(date +%Y%m%d-%H%M%S)
ROOT=$(cd "$(dirname "$0")/.." && pwd)
cd "$ROOT"

case "$WHERE" in mac|vm) ;; *) echo "where must be mac or vm" >&2; exit 2 ;; esac
[ -f "$KEY" ] || { echo "no passphrase file at $KEY" >&2; exit 2; }

# git does not hold these: untracked files, and git-ignored ones (keys, renders, backups, call logs).
# Virtualenvs and caches are rebuilt, so they are left out.
repo_list() {
  git ls-files --others --exclude-standard
  git ls-files --others --ignored --exclude-standard --directory
}
repo_list | grep -v -E '(^|/)(\.venv|__pycache__|\.DS_Store)(/|$)' | sort -u > "${TMPDIR:-/tmp}/backup-list.$$"
trap 'rm -f "${TMPDIR:-/tmp}/backup-list.$$"' EXIT
LIST="${TMPDIR:-/tmp}/backup-list.$$"

if [ "$DRY" = "--dry-run" ]; then
  echo "$(wc -l < "$LIST" | tr -d ' ') paths in the repo:"
  tar -cf - -T "$LIST" 2>/dev/null | wc -c | awk '{printf "about %.1f GB before encryption\n", $1/1073741824}'
  if [ "$WHERE" = "vm" ]; then echo "plus /home/nathan/backups and the seaweedfs-data volume"; fi
  exit 0
fi

DEST="$BUCKET/$WHERE/$STAMP"
echo "repo files -> $DEST/repo.tar.gpg"
tar -cf - -T "$LIST" | gpg --batch --yes --symmetric --cipher-algo AES256 \
  --passphrase-file "$KEY" | gcloud storage cp - "$DEST/repo.tar.gpg"

if [ "$WHERE" = "vm" ]; then
  echo "/home/nathan/backups -> $DEST/home-backups.tar.gpg"
  sudo tar -C /home/nathan -cf - backups | gpg --batch --yes --symmetric --cipher-algo AES256 \
    --passphrase-file "$KEY" | gcloud storage cp - "$DEST/home-backups.tar.gpg"

  echo "seaweedfs-data volume -> $DEST/seaweedfs-data.tar.gpg"
  sudo docker run --rm -v writers-room_seaweedfs-data:/v alpine tar -C /v -cf - . \
    | gpg --batch --yes --symmetric --cipher-algo AES256 --passphrase-file "$KEY" \
    | gcloud storage cp - "$DEST/seaweedfs-data.tar.gpg"
fi
echo "done: $DEST"
