#!/usr/bin/env bash
set -euo pipefail

staging=$(mktemp -d)
trap 'rm -rf "$staging"' EXIT
cp -a k8s "$staging/"
cat >> "$staging/k8s/kustomization.yaml" <<YAML
images:
  - name: smart-home-backend
    newName: $IMAGE_PREFIX/smart-home-backend
    newTag: "$GITHUB_SHA"
  - name: smart-home-frontend
    newName: $IMAGE_PREFIX/smart-home-frontend
    newTag: "$GITHUB_SHA"
YAML

if git ls-remote --exit-code --heads origin gitops >/dev/null; then
  git fetch origin gitops
  git switch -C gitops FETCH_HEAD
else
  result=$?
  test "$result" = 2
  git switch --orphan gitops
fi

git rm -rf --ignore-unmatch k8s >/dev/null
mkdir -p k8s
cp -a "$staging/k8s/." k8s/
git add -A k8s
if git diff --cached --quiet; then
  exit 0
fi
git -c user.name=github-actions -c user.email=41898282+github-actions[bot]@users.noreply.github.com \
  commit -m "Deploy smart-home $GITHUB_SHA"
git push origin HEAD:refs/heads/gitops
