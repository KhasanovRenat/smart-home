# Безопасность

FastAPI выдаёт подписанный JWT на 30 минут. Локальные учётные данные из `.env.example` предназначены для демонстрации. При развертывании подставьте свои пароли и ключ подписи. В Kubernetes NetworkPolicy разрешает доступ к FastAPI из frontend, Traefik и Prometheus. Доступ к PostgreSQL разрешён из backend. В Terraform RDS закрыта снаружи, доступ к EC2 идёт через AWS SSM, для RDS настроено ежедневное резервное копирование в AWS Backup. Trivy проверяет оба образа в CI и показывает результаты в логах workflow.

## Vault для EKS

Выполните после подготовки кластера и создания `k8s/storage-class.yaml`. Это учебная конфигурация Vault внутри кластера. Для доступа извне настройте TLS и укажите HTTPS в VaultConnection.

```bash
helm repo add hashicorp https://helm.releases.hashicorp.com
helm repo update
helm upgrade --install vault hashicorp/vault -n vault --create-namespace \
  --set injector.enabled=false --set server.authDelegator.enabled=true \
  --set server.dataStorage.storageClass=smart-home-gp3
helm upgrade --install vault-secrets-operator hashicorp/vault-secrets-operator \
  -n vault --wait
```

Дождитесь состояния Running у `vault-0`. Инициализируйте хранилище и сохраните ключи разблокировки и root token:

```bash
kubectl -n vault exec vault-0 -- vault operator init
kubectl -n vault exec -it vault-0 -- vault operator unseal
kubectl -n vault exec -it vault-0 -- vault operator unseal
kubectl -n vault exec -it vault-0 -- vault operator unseal
kubectl -n vault exec -it vault-0 -- vault login
```

Каждый раз вводите отдельный ключ разблокировки, а при входе — root token. Включите Kubernetes-аутентификацию и подготовьте политику чтения:

```bash
kubectl -n vault exec vault-0 -- vault auth enable kubernetes
kubectl -n vault exec vault-0 -- vault write auth/kubernetes/config \
  kubernetes_host=https://kubernetes.default.svc
kubectl -n vault exec vault-0 -- vault secrets enable -path=secret kv-v2
kubectl -n vault exec -i vault-0 -- vault policy write smart-home - < k8s/vault/policy.hcl
kubectl -n vault exec vault-0 -- vault write auth/kubernetes/role/smart-home \
  bound_service_account_names=smart-home-vault \
  bound_service_account_namespaces=smart-home audience=vault policies=smart-home ttl=1h
```

Введите значения в текущем терминале и передайте их в Vault:

```bash
for name in DB_PASSWORD APP_PASSWORD JWT_SECRET GRAFANA_ADMIN_PASSWORD; do
  read -rsp "$name: " "$name"
  printf '\n'
  export "$name"
done
python3 -c 'import json, os; print(json.dumps({key: os.environ[key] for key in ("DB_PASSWORD", "APP_PASSWORD", "JWT_SECRET", "GRAFANA_ADMIN_PASSWORD")}))' \
  | kubectl -n vault exec -i vault-0 -- vault kv put -mount=secret smart-home -
unset DB_PASSWORD APP_PASSWORD JWT_SECRET GRAFANA_ADMIN_PASSWORD
kubectl apply -f k8s/vault/resources.yaml
kubectl -n smart-home get vaultstaticsecret,secret
```

Ключ `JWT_SECRET` должен содержать минимум 32 байта. Оператор синхронизирует запись в Kubernetes Secret `smart-home-secrets`, который читают backend, PostgreSQL и Grafana.
