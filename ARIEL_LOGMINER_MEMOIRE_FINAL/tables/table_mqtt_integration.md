| Brique | Etat dans Logminer | Preuve locale | Limite a declarer |
| --- | --- | --- | --- |
| Broker MQTT | Integre via Mosquitto local | `docker-compose.mqtt.yml`, `docker/mosquitto/mosquitto.conf` | Configuration anonyme reservee au laboratoire local |
| Bus MQTT | Integre comme bus pub/sub optionnel | `MqttMessageBus` dans `src/logminer/agents/bus.py` | Pas de relecture historique comme Redis Streams |
| Endpoints API | Integres pour verification et publication | `/mqtt/health`, `/mqtt/publish` | Usage de test/control-plane, pas ingestion SOC publique |
| Contrat de message | Reutilise `AgentMessage` | Topics `logminer/events/<target>/<message_type>` | Schema a versionner si des collecteurs externes publient |
| Smoke test | Publication recue par subscriber MQTT | `mqtt-pubsub-smoke`, topic `logminer/events/collector/mqtt.pubsub.smoke` | Test fonctionnel court, pas benchmark de debit |
| Positionnement | Collecteurs legers, IoT/reseau local, notifications temps reel | Complementaire a Redis Streams | Redis reste preferable pour jobs persistants et workers |
