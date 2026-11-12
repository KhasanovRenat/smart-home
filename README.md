# Лабораторная работа № 2. DevOps-пайплайн для умного дома

## Запуск на Windows

1. Установите и запустите Docker Desktop с Linux-контейнерами.
2. Распакуйте архив. Откройте PowerShell в папке, где лежит `docker-compose.yml`.
3. Выполните:

   ```powershell
   Copy-Item .env.example .env
   docker compose up --build -d --wait
   docker compose ps
   ```

| Сервис | Адрес | Данные для входа |
|---|---|---|
| Умный дом | http://localhost:3000 | `admin` / `lab-admin-2026` |
| Swagger FastAPI | http://localhost:8000/docs | Кнопка Authorize, данные как для умного дома |
| Prometheus | http://localhost:9090/targets | Цель `fastapi` |
| Grafana | http://localhost:3001 | `admin` / `admin` |
| Alertmanager | http://localhost:9093 | Учебные оповещения |

В интерфейсе включите умный свет и обновите страницу. После повторного входа проверьте, что состояние сохранилось. В Grafana откройте **Dashboards → Умный дом · FastAPI**. Источник Prometheus и дашборд подключаются автоматически. Для остановки выполните `docker compose down`. Данные PostgreSQL сохраняются в томе.

## Остальные разделы

- [Архитектура](docs/architecture.md)
- [GitHub Actions, AWS EC2/RDS, EKS и ArgoCD](docs/deployment.md)
- [Prometheus, Grafana, Loki и Alertmanager](docs/monitoring.md)
- [JWT, Vault и Network Policies](docs/security.md)

Для локального запуска достаточно Docker Desktop. Облачные этапы запускаются после настройки вашего репозитория, Docker Hub и AWS.
