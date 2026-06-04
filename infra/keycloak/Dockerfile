FROM quay.io/keycloak/keycloak:26.6@sha256:f9ba7b2af90db8dc749a57ca9aedca51e840cb9224441ab546a968da941da900 AS builder

# Enable health and metrics support
ENV KC_HEALTH_ENABLED=true
ENV KC_METRICS_ENABLED=true

# Configure a database vendor
ENV KC_DB=postgres

WORKDIR /opt/keycloak
# Optimized build for production
RUN /opt/keycloak/bin/kc.sh build

FROM quay.io/keycloak/keycloak:26.6@sha256:f9ba7b2af90db8dc749a57ca9aedca51e840cb9224441ab546a968da941da900
COPY --from=builder /opt/keycloak/ /opt/keycloak/

# Keycloak will run in proxy mode.
# Configuration is handled via environment variables in docker-compose.

ENTRYPOINT ["/opt/keycloak/bin/kc.sh"]
