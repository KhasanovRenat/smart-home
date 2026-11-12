# Архитектура

| Компонент | Назначение |
|---|---|
| React / Nginx | Вход, список устройств, включение и выключение. В Docker Compose Nginx проксирует `/api/` в FastAPI. |
| FastAPI | Выдаёт JWT, управляет устройствами, записывает показания и публикует метрики. |
| PostgreSQL | Хранит таблицы устройств и измерений. Стартовые устройства создаются однократно. |
| Prometheus / Grafana | Prometheus опрашивает `/metrics`, Grafana показывает доступность, частоту запросов и время ответа. |
| Loki / Alloy | В EKS Alloy читает логи контейнеров FastAPI через Kubernetes API и отправляет их в Loki. |
| GitHub Actions / Terraform / ArgoCD | Actions собирает образы, Terraform готовит EC2 и RDS, ArgoCD синхронизирует манифесты в EKS. |

Контракты API доступны в Swagger `/docs`. Устройство переключается атомарным запросом в PostgreSQL. Чтение и запись защищены JWT.

| Метод и путь | Действие |
|---|---|
| `POST /token` | Получить токен по логину и паролю |
| `GET /devices` | Получить список устройств |
| `POST /devices/{id}/toggle` | Переключить устройство |
| `POST /devices/{id}/readings` | Записать измерение, например `{"value":22.5}` |
| `GET /devices/{id}/readings` | Получить до 100 последних измерений |
| `GET /health` | Проверить подключение к PostgreSQL |
| `GET /metrics` | Получить метрики Prometheus |

Маршруты приложения также доступны с префиксом `/api`. В EKS Traefik направляет `/api` в FastAPI, а `/` в React. HPA масштабирует backend от 2 до 10 реплик при цели 70% CPU. Состояния устройств сохраняются в общей базе. В Kubernetes PostgreSQL использует постоянный том EBS. При развертывании на EC2 используется Amazon RDS.
