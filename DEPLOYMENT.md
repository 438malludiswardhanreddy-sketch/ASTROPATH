# Deployment Notes (quick)

Production checklist (short):

- Set `FLASK_DEBUG = False` in `config.py` and disable any debug features.
- Use a WSGI server (e.g. `waitress` or `gunicorn`) — do not use Flask dev server in production.
- Use nginx (or other reverse proxy) for TLS termination and to serve static assets.
- Replace SQLite with a production DB (Postgres) when concurrent writes are expected.
- Run the app under a process manager (`systemd`, `supervisor`, or Docker) and configure logs/rotation.

Docker (quick):

1. Build image:
```
docker build -t astropath-dashboard .
```

2. Run (exposes port 5000):
```
docker run -p 5000:5000 astropath-dashboard
```

Systemd (quick):

1. Place the unit file `deploy/astropath.service` under `/etc/systemd/system/` (edit paths).
2. Reload and enable:
```
sudo systemctl daemon-reload
sudo systemctl enable --now astropath.service
```

Using `waitress` (Windows-friendly):
```
pip install waitress
waitress-serve --call 'src.dashboard:create_app' --listen=0.0.0.0:5000
```

Security & reliability notes:

- Serve behind nginx to enable TLS and client-side caching.
- Configure log rotation (e.g. `logrotate`) for application logs.
- Monitor the process with systemd or Prometheus metrics as needed.
