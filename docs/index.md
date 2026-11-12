# Умный дом

Учебная система для управления умным светом и термостатом. Веб-интерфейс работает через FastAPI. PostgreSQL хранит состояния устройств и показания датчиков.

Для запуска на Windows откройте PowerShell в корне проекта при работающем Docker Desktop:

```powershell
Copy-Item .env.example .env
docker compose up --build -d --wait
```

Откройте [умный дом](http://localhost:3000) и войдите как `admin` с паролем `lab-admin-2026`. Swagger доступен на [порту 8000](http://localhost:8000/docs), Prometheus на [9090](http://localhost:9090), Grafana на [3001](http://localhost:3001).

Для сборки этой документации выполните из корня проекта:

```bash
python -m pip install -r docs/requirements.txt
mkdocs build --strict
```
