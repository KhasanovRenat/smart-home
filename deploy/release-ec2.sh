#!/usr/bin/env bash
set -euo pipefail

instance=$(terraform -chdir=terraform output -raw instance_id)
db_host=$(terraform -chdir=terraform output -raw db_host)
db_secret=$(terraform -chdir=terraform output -raw db_secret_arn)
archive="$RUNNER_TEMP/smart-home.tar.gz"
git archive --format=tar.gz -o "$archive" "$GITHUB_SHA" \
  docker-compose.yml backend frontend monitoring k8s/config deploy/ec2-start.sh
uri="s3://$TF_VAR_release_bucket/releases/$GITHUB_SHA.tar.gz"
aws s3 cp "$archive" "$uri" --only-show-errors

for attempt in $(seq 1 60); do
  status=$(aws ssm describe-instance-information \
    --filters "Key=InstanceIds,Values=$instance" \
    --query 'InstanceInformationList[0].PingStatus' --output text)
  if [ "$status" = "Online" ]; then
    break
  fi
  sleep 10
done
test "$status" = "Online"

parameters=$(python3 - "$uri" "$AWS_DEFAULT_REGION" "$GITHUB_SHA" "$db_host" \
  "$db_secret" "$TF_VAR_app_secret_arn" "$IMAGE_PREFIX" <<'PY'
import json
import shlex
import sys

uri, region, sha, db_host, db_secret, app_secret, prefix = sys.argv[1:]
commands = [
    "set -eu",
    "umask 077",
    "cloud-init status --wait",
    "install -d -m 700 /opt/smart-home",
    "cd /opt/smart-home",
    "archive=$(mktemp)",
    """trap 'rm -f "$archive"' EXIT""",
    shlex.join(["aws", "s3", "cp", "--region", region, uri]) + ' "$archive" --only-show-errors',
    'tar -xzf "$archive"',
    shlex.join(["bash", "deploy/ec2-start.sh", region, sha, db_host, db_secret, app_secret, prefix]),
]
print(json.dumps({"commands": commands}))
PY
)
command_id=$(aws ssm send-command --instance-ids "$instance" \
  --document-name AWS-RunShellScript --parameters "$parameters" \
  --query Command.CommandId --output text)
for attempt in $(seq 1 90); do
  status=$(aws ssm get-command-invocation --command-id "$command_id" \
    --instance-id "$instance" --query Status --output text 2>/dev/null || true)
  case "$status" in
    Success) echo "Проверка /api/health на EC2 прошла"; exit 0 ;;
    Failed|Cancelled|TimedOut|Cancelling)
      aws ssm get-command-invocation --command-id "$command_id" --instance-id "$instance" \
        --query StandardErrorContent --output text >&2
      exit 1 ;;
  esac
  sleep 10
done
echo "Тайм-аут развертывания EC2 ($command_id)" >&2
exit 1
