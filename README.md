# Jarvis Sentinel

Plataforma de automação GPS com foco em geofencing, leitura de coordenadas e integração com outros serviços.

## Arquitetura inicial

- `python/jarvis_gps.py`: núcleo em Python, com cálculo de distância, geofencing e modo simulado.
- `typescript/gps_client.ts`: cliente tipado para enviar posições a uma API futura.
- `web/index.html`: painel 3D inicial inspirado no “God’s Eye View”, com camadas simuladas de aviões, navios, satélites e trânsito, filtros e rotas.
- `.env.example`: credenciais e endpoints das fontes externas.
- `python/settings.py`: leitura segura das configurações pelo ambiente.
- `backend/app.py`: API FastAPI com health check, fontes, geofences e WebSocket de posições.
- `tests/test_gps.py`: testes do núcleo de distância e transição de geofence.
- `Dockerfile` e `docker-compose.yml`: execução local reproduzível da API.
- O projeto começa sem hardware: o modo simulado permite validar regras antes de conectar um dispositivo GPS real.

## Executar o simulador

```bash
python python/jarvis_gps.py --demo --center-lat -23.5505 --center-lon -46.6333
```

Para testar um ponto específico em relação a uma área:

```bash
python python/jarvis_gps.py --lat -23.5505 --lon -46.6333 --center-lat -23.5505 --center-lon -46.6333 --radius 250
```

Também é possível converter uma sentença NMEA `GPRMC`:

```bash
python python/jarvis_gps.py --nmea '$GPRMC,123519,A,2331.000,S,04637.998,W,0.0,0.0,230326,,,A*00' --center-lat -23.5167 --center-lon -46.6333
```

O programa informa quando o dispositivo entra ou sai da área configurada. A posição recebida deve ser tratada como dado sensível: evite registrar coordenadas reais em logs públicos.

## Abrir o painel 3D

Abra `web/index.html` em um navegador com acesso à internet. A primeira versão usa dados simulados e bibliotecas carregadas por CDN; os próximos adaptadores poderão conectar fontes públicas de voos, navios e satélites.

As fontes públicas NASA GIBS, USGS Earthquakes e CelesTrak já ficam configuradas por padrão no `.env` local. Para ativar Google Maps, Copernicus Sentinel, AISStream ou OpenSky, copie `.env.example` para `.env` e preencha as credenciais reais localmente. Valores vazios ou de exemplo não ativam conectores. Nunca publique o `.env`.

## Executar a API

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r backend/requirements.txt
uvicorn backend.app:app --reload
```

Ao iniciar a API, o painel fica disponível em `http://localhost:8000`. Endpoints principais: `GET /api/health`, `GET /api/sources`, `GET/POST /api/geofences` e `WS /ws/positions`.

Para executar com Docker: `docker compose up --build`.
Projeto Jarvis Sentinel
