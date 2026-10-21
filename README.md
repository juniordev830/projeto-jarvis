# Projeto Jarvis

Base de automação GPS com foco em geofencing, leitura de coordenadas e integração com outros serviços.

## Arquitetura inicial

- `python/jarvis_gps.py`: núcleo em Python, com cálculo de distância, geofencing e modo simulado.
- `typescript/gps_client.ts`: cliente tipado para enviar posições a uma API futura.
- O projeto começa sem hardware: o modo simulado permite validar regras antes de conectar um dispositivo GPS real.

## Executar o simulador

```bash
python python/jarvis_gps.py --demo --center-lat -23.5505 --center-lon -46.6333
```

Para testar um ponto específico em relação a uma área:

```bash
python python/jarvis_gps.py --lat -23.5505 --lon -46.6333 --center-lat -23.5505 --center-lon -46.6333 --radius 250
```

O programa informa quando o dispositivo entra ou sai da área configurada. A posição recebida deve ser tratada como dado sensível: evite registrar coordenadas reais em logs públicos.
Projeto de automação Jarvis
