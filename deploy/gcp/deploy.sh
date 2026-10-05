#!/usr/bin/env bash
# Stand up the writers' room on one GCP VM, behind HTTPS and a Basic Auth popup.
#
#   deploy/gcp/deploy.sh                 # create everything, print the URL + password
#   ROOM_PASSWORD=... deploy/gcp/deploy.sh   # choose your own password
#
# Idempotent: rerunning reuses the IP, firewall rules and VM, and redeploys the app.
set -euo pipefail

PROJECT=${PROJECT:-voltaic-quest-502915-u7}
ZONE=${ZONE:-us-central1-a}
REGION=${ZONE%-*}
NAME=${NAME:-writers-room}
MACHINE=${MACHINE:-e2-standard-2}
ROOM_USER=${ROOM_USER:-nathan}
ROOM_PASSWORD=${ROOM_PASSWORD:-$(openssl rand -base64 15 | tr -d '/+=' | cut -c1-16)}
REPO=${REPO:-https://github.com/nathanverrill/graphic-novel-writers-room.git}

g() { gcloud --project "$PROJECT" "$@"; }

echo "== static IP"
g compute addresses describe "$NAME-ip" --region "$REGION" >/dev/null 2>&1 ||
  g compute addresses create "$NAME-ip" --region "$REGION"
IP=$(g compute addresses describe "$NAME-ip" --region "$REGION" --format='value(address)')
HOST=${IP//./-}.sslip.io
echo "   $IP  ->  https://$HOST"

echo "== firewall: 80 and 443 only"
g compute firewall-rules describe allow-http >/dev/null 2>&1 ||
  g compute firewall-rules create allow-http --allow tcp:80 --target-tags http-server
g compute firewall-rules describe allow-https >/dev/null 2>&1 ||
  g compute firewall-rules create allow-https --allow tcp:443 --target-tags https-server

echo "== VM"
g compute instances describe "$NAME" --zone "$ZONE" >/dev/null 2>&1 ||
  g compute instances create "$NAME" \
    --zone "$ZONE" --machine-type "$MACHINE" \
    --image-family debian-12 --image-project debian-cloud \
    --boot-disk-size 50GB --boot-disk-type pd-balanced \
    --address "$IP" --tags http-server,https-server

echo "== waiting for SSH"
for i in $(seq 1 30); do
  g compute ssh "$NAME" --zone "$ZONE" --command true >/dev/null 2>&1 && break
  sleep 5
done

echo "== installing and starting the room (first build takes a few minutes)"
g compute ssh "$NAME" --zone "$ZONE" --command "
  set -euo pipefail
  command -v docker >/dev/null || curl -fsSL https://get.docker.com | sudo sh
  if [ ! -d writers-room ]; then git clone $REPO writers-room; else git -C writers-room pull --ff-only; fi
  cd writers-room

  # env: provider URL + model; the API key is pasted in the UI and lands in secrets/keys.json
  if [ ! -f .env ]; then
    cp .env.example .env
    sed -i 's|^OPENAI_BASE_URL=.*|OPENAI_BASE_URL=https://openrouter.ai/api/v1|' .env
    sed -i 's|^OPENAI_MODEL=.*|OPENAI_MODEL=openai/gpt-5.6-luna|' .env
    sed -i 's|^OPENAI_API_KEY=.*|OPENAI_API_KEY=|' .env
  fi

  # the containers run as this user, so the room's output stays editable over SSH
  grep -q '^ROOM_UID=' .env || printf 'ROOM_UID=%s\nROOM_GID=%s\n' \"\$(id -u)\" \"\$(id -g)\" >> .env
  mkdir -p secrets debug logs campaigns sheets/characters art/data
  sudo chown -R \"\$(id -u):\$(id -g)\" secrets debug logs campaigns sheets/characters art/data

  # Caddy: HTTPS on the sslip.io name, Basic Auth popup in front of everything
  HASH=\$(sudo docker run --rm caddy:2 caddy hash-password --plaintext '$ROOM_PASSWORD')
  printf '%s {\n    basic_auth {\n        %s %s\n    }\n    reverse_proxy app:8000\n}\n' \
    '$HOST' '$ROOM_USER' \"\$HASH\" | sudo tee deploy/gcp/Caddyfile >/dev/null

  sudo docker compose -f docker-compose.yml -f deploy/gcp/caddy.yml up -d --build
"

echo
echo "done: https://$HOST"
echo "user: $ROOM_USER   password: $ROOM_PASSWORD"
echo "(paste your provider API key in the UI once it loads)"
