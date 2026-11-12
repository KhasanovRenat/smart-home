# Развертывание

Команды облачного раздела рассчитаны на Bash, например WSL или AWS CloudShell. Для локального Docker Compose подходят команды PowerShell с главной страницы.

## GitHub Actions

Создайте отдельный репозиторий и загрузите в корень все файлы проекта, включая каталог `.github`. Рабочая ветка — `main`. На pull request workflow проверяет FastAPI с PostgreSQL, собирает React и два Docker-образа, запускает Trivy и проверяет Terraform. Публикация включается переменными репозитория.

| Переменная или Secret | Значение |
|---|---|
| Variable `PUBLISH_IMAGES` | `true` для публикации образов из main |
| Variable `DOCKER_HUB_NAMESPACE` | Логин или пространство имён Docker Hub |
| Secret `DOCKER_HUB_TOKEN` | Токен с правом публикации в выбранное пространство |
| Variable `DEPLOY_AWS` | `true` для Terraform и развертывания на EC2 |
| Variable `AWS_REGION` | По умолчанию `eu-central-1` |
| Variables `TF_STATE_BUCKET`, `APP_SECRET_ARN` | Существующий S3-бакет и ARN секрета приложения |
| Secrets `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY` | Учётные данные для Terraform и SSM |
| Variable `DEPLOY_EKS` | `true` для обновления ветки `gitops` |
| Variable `PUBLISH_DOCS` | `true` для публикации MkDocs |

На Docker Hub подготовьте публичные репозитории `smart-home-backend` и `smart-home-frontend`. Actions публикует образы с тегом SHA коммита. Для публикации документации в **Settings → Pages → Build and deployment → Source** выберите **GitHub Actions**.

## AWS EC2 и RDS

В выбранном регионе подготовьте VPC с общедоступными подсетями в двух зонах доступности (конфигурация по умолчанию использует default VPC), закрытый S3-бакет для состояния Terraform и артефактов и JSON-секрет в AWS Secrets Manager. Ключи секрета — `APP_PASSWORD`, `JWT_SECRET` (от 32 байт), `GRAFANA_ADMIN_PASSWORD` и, при необходимости, `APP_USERNAME`. Используйте отдельные однострочные значения. Бакет и секрет должны быть доступны используемым ролям. Для учебной конфигурации используется шифрование сервисными ключами AWS.

Порядок в workflow — `terraform init` с S3, `terraform plan`, `terraform apply`, передача релиза через S3 и запуск Compose на EC2 через Systems Manager. RDS находится в приватном доступе. Для доступа к веб-интерфейсу установите Session Manager plugin и пробросьте порт:

```bash
aws ssm start-session --region eu-central-1 --target i-REPLACE_ME \
  --document-name AWS-StartPortForwardingSession \
  --parameters '{"portNumber":["80"],"localPortNumber":["3000"]}'
```

Замените ID на значение вывода Terraform `instance_id`. Откройте [localhost:3000](http://localhost:3000). Учётные данные берутся из секрета приложения. После ротации мастер-пароля RDS повторите workflow, чтобы обновить пароль контейнера backend.

## EKS, Traefik и ArgoCD

1. Установите `aws`, `eksctl`, `kubectl` и `helm`. Создайте кластер и класс хранилища:

   ```bash
   eksctl create cluster -f deploy/eks.yaml
   kubectl apply -f k8s/namespace.yaml -f k8s/storage-class.yaml
   ```

2. Установите Vault и подготовьте секрет по разделу [«Безопасность»](security.md).
3. Установите Traefik и ArgoCD:

   ```bash
   helm repo add traefik https://traefik.github.io/charts
   helm repo add argo https://argoproj.github.io/argo-helm
   helm repo update
   helm upgrade --install traefik traefik/traefik -n traefik --create-namespace --set service.type=ClusterIP --wait
   helm upgrade --install argocd argo/argo-cd -n argocd --create-namespace --wait
   ```

4. Запустите workflow **Smart Home CI/CD** в ветке `main` с включенными `PUBLISH_IMAGES` и `DEPLOY_EKS`. Он создаст или обновит ветку `gitops`. Подставьте URL вашего репозитория вместо `OWNER/REPOSITORY` в `deploy/argocd-application.yaml`. Для приватного репозитория сначала подключите его в ArgoCD с доступом на чтение. Примените Application:

   ```bash
   kubectl apply -f deploy/argocd-application.yaml
   kubectl -n argocd get application smart-home
   kubectl -n smart-home get pods,hpa,ingress
   ```

   Для ручной установки без ArgoCD возьмите `k8s/` из ветки `gitops` и выполните `kubectl apply -k k8s/`.

5. Проверьте Ingress. В отдельном терминале запустите `kubectl -n traefik port-forward svc/traefik 8088:80`, затем выполните:

   ```bash
   curl -H 'Host: smart-home.example.com' http://127.0.0.1:8088/api/health
   ```

Ресурсы AWS тарифицируются. После демонстрации отключите переменные деплоя. Для очистки EKS удалите стенд через `eksctl delete cluster -f deploy/eks.yaml` и проверьте, остались ли тома EBS с политикой Retain. Для Terraform используйте `terraform destroy` с тем же S3-состоянием и переменными. Хранилище AWS Backup с оставшимися точками восстановления нужно очистить перед его удалением.
