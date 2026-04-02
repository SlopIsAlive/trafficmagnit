# trafficmagnit

Currency exchange rate tracker. Periodically fetches UAH exchange rates from Monobank, stores history in PostgreSQL, and exposes a REST API to manage which currencies to track.

**Stack:** Django + DRF, Celery + RabbitMQ, Redis, PostgreSQL

## API

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/currencies/` | List tracked currencies with current rate |
| GET | `/currencies/available/` | All ISO 4217 currencies not yet tracked |
| POST | `/currencies/add/` | Start tracking a currency `{"iso_code": 840}` |
| POST | `/currencies/<iso_code>/enable/` | Resume tracking |
| POST | `/currencies/<iso_code>/disable/` | Pause tracking |
| GET | `/rates/<iso_code>/history/?from_date=&to_date=` | Rate history for a date range |

Swagger UI at `/api/schema/swagger-ui/`

## Run
```bash
cp .env.example .env
docker compose up --build
```

That's it. Migrations run automatically before the app starts.

Management command usage example:

python manage.py export_rates_csv
python manage.py export_rates_csv --output /tmp/rates.csv


## Notes

`iso4217` is used purely for currency validation and lookup. If you'd rather not have the dependency, it's easy to replace — the ISO 4217 standard rarely changes, so hardcoding the relevant currency codes directly is a reasonable alternative.
