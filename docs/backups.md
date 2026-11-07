# Backups

What must not be lost, where it lives, and how it is copied. Written 2026-11-06 from a read-only check of the Mac, the VM and the GCP project.

## What is protected by git

Campaign text, code, docs, the book tools, the layouts and the proof state where tracked. Git holds the history, but only for what is committed. Push to `origin` to keep it off the machine.

## What is not in git (the gap)

| Where | What | Size | Protected today |
|---|---|---|---|
| VM `/home/nathan/backups/` | Pre-change copies of the book, the proof and the app (the only copies of several states) | 2.7 GB | No |
| VM `.env`, `secrets/`, `logs/usage.jsonl` | Keys, settings, usage ledger | small | Usage ledger in SeaweedFS only |
| VM `campaigns/` untracked | Lettered pages, call logs, `previous/` copies, renders | part of 9.8 GB | No |
| VM Docker volume `seaweedfs-data` | Object store (usage ledger) | unknown | No |
| VM Docker volume `opensearch-data` | Search index | unknown | Rebuildable from the files |
| VM disk `writers-room` (50 GB) | Everything above | 50 GB | **No snapshots.** The project's 14-day daily schedule (`default-schedule-1`) exists but is attached to other disks only |
| Mac `backups/` | Hackathon bucket pulls, with API keys inside | 1.5 GB | No (local only, by design) |
| Mac `debug/` | Debug output | 881 MB | No |
| Mac `campaigns/prosperity-book/renders/` | Rendered pages | 824 MB | No |
| Mac `secrets/`, `.env`, `sheets/characters/` (character builds) | Keys, settings, user work | small | No |
| Mac `/private/tmp/claude-501/` (session scratchpad) | Session files | 2.3 GB | No; macOS clears `/tmp` |
| Mac Time Machine | Whole disk | — | **No destination configured** |

## The plan

1. **VM disk snapshots.** Attach the existing `default-schedule-1` policy to the `writers-room` disk: daily, 14 days kept. Restores the whole disk, including the Docker volumes and `/home/nathan/backups`. One command, run only with a go-ahead:
   `gcloud compute disks add-resource-policies writers-room --resource-policies default-schedule-1 --zone us-central1-a --project voltaic-quest-502915-u7`
   Before any deploy, take a labelled manual snapshot as well.
2. **Off-machine copy of the non-git files.** A private bucket in the same project, with object versioning on and a lifecycle rule. A script run daily on the VM copies `.env`, `secrets/`, `logs/`, `/home/nathan/backups/` and the untracked campaign output. Archives holding keys are encrypted before upload.
3. **Mac copy.** `scripts/backup.sh mac` sends the non-git files to the bucket. Time Machine is not set up (no drive). Copy `backups/`, `debug/`, the renders, `secrets/`, `.env` and `sheets/characters/` in the same run. Move anything worth keeping out of `/private/tmp` into a folder the backup covers.
4. **Restore test.** Once a quarter: restore one file from each tier and open it. A backup that has not been restored is not known to work.

## Rules

- Keys and `.env` never go into git or into an unencrypted bucket.
- Nothing is pushed to a public place. The bucket stays private.
- Before any VM change: a snapshot first (step 1), as the existing rule says.
- Restores go to a new folder first, never over the live files.

## Status (2026-11-06)

- Done: VM disk snapshots. `default-schedule-1` (daily, 14 days) is attached to the `writers-room` disk.
- Done: bucket `gs://writers-room-backups-voltaic-quest-502915-u7`. Private (public access prevention enforced), uniform access, versioning on, noncurrent versions deleted after 90 days.
- Done: `scripts/backup.sh`. The Mac's non-git files (1,043 paths, about 5.7 GB) were sent to `mac/<stamp>/repo.tar.gpg`.
- Passphrase: `~/.config/writers-room-backup/key` on the Mac, mode 600. **Save a copy in a password manager.** Without it nothing in the bucket can be opened.
- Not done: the VM copy. It needs the passphrase file on the VM and a daily cron entry. Both change the VM, so they wait for a go-ahead. The first run would send `/home/nathan/backups` (2.7 GB) and the SeaweedFS volume.
- Not done: step 3, a Mac drive for Time Machine. You chose the bucket only.
- Not done: the restore test (step 4). Do it once before relying on this.
