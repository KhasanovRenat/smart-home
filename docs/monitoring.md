# Мониторинг и логи

- Prometheus опрашивает FastAPI раз в 15 секунд. Страница [Targets](http://localhost:9090/targets) показывает состояние цели. В EKS DNS-сервис `backend-metrics` позволяет собирать метрики каждой реплики.
- Grafana получает источник Prometheus и дашборд **Умный дом · FastAPI** при запуске. Локальный доступ — [localhost:3001](http://localhost:3001). Выполните несколько действий в интерфейсе, чтобы появились показатели частоты и длительности запросов.
- Alertmanager принимает оповещения о недоступности FastAPI или нагрузке выше 80% одного ядра. Для демонстрации остановите backend через `docker compose stop backend`. Через 1–2 минуты проверьте [Prometheus Alerts](http://localhost:9090/alerts) и [Alertmanager](http://localhost:9093). Затем выполните `docker compose start backend`.
- В EKS откройте Grafana через `kubectl -n smart-home port-forward svc/grafana 3001:3000`. В **Explore → Loki** выполните запрос `{container="backend"}`. Для фильтрации можно добавить `|= "ERROR"`. Alloy собирает логи FastAPI через Kubernetes API. Учебные хранилища мониторинга в EKS используют временные тома.

Для сбора логов выбран поддерживаемый Grafana Alloy. Promtail из примера методички снят с поддержки. [Документация Grafana](https://grafana.com/docs/grafana-cloud/send-data/alloy/set-up/migrate/from-promtail/).
