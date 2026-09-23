#!/bin/sh
# Start (or rebuild) another instance of the room: scripts/instance.sh <name> <port>
# Makes instances/<name>/ from the first instance's files the first time.
set -e
name=${1:?name, e.g. three}; port=${2:?port, e.g. 8020}
cd "$(dirname "$0")/.."
if [ ! -d "instances/$name" ]; then
  mkdir -p "instances/$name/sheets-characters" "instances/$name/debug"
  cp -R campaigns "instances/$name/campaigns"; cp -R agents "instances/$name/agents"; cp pricing.json "instances/$name/pricing.json"
  echo "instances/$name: made from the first instance's campaigns, agents and pricing"
fi
INSTANCE=$name PORT=$port docker compose -p "writers-room-$name" -f docker-compose.yml -f docker-compose.instance.yml up -d --build
echo "http://localhost:$port"
