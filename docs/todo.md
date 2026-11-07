# To-do

Written 2026-11-06. Items marked **(go-ahead)** change the VM or a shared place, so they wait for a yes.

## Backups (see docs/backups.md)
- [ ] Save the passphrase `~/.config/writers-room-backup/key` in a password manager.
- [ ] Restore test: open the Mac archive `mac/20261106-150740/repo.tar.gpg` into a new folder and check a few files.
- [ ] Confirm the first VM disk snapshot is made at 03:00 UTC.
- [ ] **(go-ahead)** VM copy: put the passphrase file on the VM, run `scripts/backup.sh vm` once by hand, then add a daily cron job.
- [ ] Time Machine on an external drive, if you get one (you chose the bucket only for now).
- [ ] Move anything worth keeping out of `/private/tmp` (session scratchpad, 2.3 GB, cleared by macOS).
- [ ] Quarterly restore test, one file from each tier.

## Git
- [ ] **(go-ahead)** Push the three local commits (`f663fbf`, `8af52ce`, `2b9ca69`) and `docs/backups.md` once it is committed.
- [ ] Decide how to handle tracked `previous/` folders, call logs and images (about 25,000 files). Untracking them removes rollback copies from the VM on its next pull, so do it with a backup first.
- [ ] Decide on the 7 modified lock and plate PNGs. The new versions are about twice the size.
- [ ] Decide whether to commit the untracked art inputs: prosperity-book style locks, plates, props, reference images, and the Bob script PDF.

## VM
- [ ] **(go-ahead)** Pull `274fafe` (ops notes) and the search fix onto the VM, then deploy it as the notes describe.
- [ ] **(go-ahead)** Change `OPENSEARCH_URL` in the VM's `.env` from `localhost:9200` to `opensearch:9200`, then restart. Search does not work until this is done.
- [ ] Re-run the VM's git status: 53 changed or untracked files, to be sorted into "keep", "commit" or "ignore".

## Book (Prosperity)
- [ ] Render status: the last run showed 34 of 43 pages failed (pages 40–78). Check the output by eye before relying on it.
- [ ] Page 37, panel 2: "Anything not worth having" has no tail drawn by Sunburst.
- [ ] Apply the proof QA findings for pages 36–59: tails pointing at the wrong figure, reading order, covered faces.
- [ ] Bob's punctuation on p39 and p44 was flagged, not changed. Ask before changing anything in Bob's text.
