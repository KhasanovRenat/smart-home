#!/usr/bin/env bash
set -euo pipefail
umask 077

region=$1
sha=$2
db_host=$3
db_secret_arn=$4
app_secret_arn=$5
image_prefix=$6

cd /opt/smart-home

python3 - "$region" "$db_host" "$db_secret_arn" "$app_secret_arn" "$image_prefix" "$sha" <<'PY'
import json
import os
import subprocess
import sys
from pathlib import Path

region, db_host, db_secret_arn, app_secret_arn, image_prefix, sha = sys.argv[1:]


def get_secret(arn):
    raw = subprocess.check_output([
        "aws", "secretsmanager", "get-secret-value", "--region", region,
        "--secret-id", arn, "--query", "SecretString", "--output", "text",
    ], text=True)
    return json.loads(raw)


db = get_secret(db_secret_arn)
app = get_secret(app_secret_arn)
env = {
    "DB_HOST": db_host,
    "DB_USER": db["username"],
    "DB_PASSWORD": db["password"],
    "DB_SSLMODE": "require",
    "APP_USERNAME": app.get("APP_USERNAME", "admin"),
    "APP_PASSWORD": app["APP_PASSWORD"],
    "JWT_SECRET": app["JWT_SECRET"],
    "GRAFANA_ADMIN_PASSWORD": app["GRAFANA_ADMIN_PASSWORD"],
    "BACKEND_IMAGE": f"{image_prefix}/smart-home-backend:{sha}",
    "FRONTEND_IMAGE": f"{image_prefix}/smart-home-frontend:{sha}",
    "FRONTEND_PORT": "80",
}
lines = []
for name, value in env.items():
    if "\n" in value or "\r" in value:
        raise ValueError(f"{name} must be a single-line value")
    escaped = value.replace("'", "\\'")
    lines.append(f"{name}='{escaped}'")
temporary = Path(".env.new")
temporary.write_text("\n".join(lines) + "\n", encoding="utf-8")
os.chmod(temporary, 0o600)
temporary.replace(".env")
PY

docker compose up --no-build --pull always -d --wait --wait-timeout 180
curl --fail --silent http://127.0.0.1/api/health
