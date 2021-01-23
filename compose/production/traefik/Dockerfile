FROM traefik:v2.2.11
RUN mkdir -p /etc/traefik/acme \
  && touch /etc/traefik/acme/acme.json \
  && chmod 600 /etc/traefik/acme/acme.json
# Each translation tool instance have different reqreuiements - this is why we can't include that file
# COPY ./compose/production/traefik/traefik-https-example.yml /etc/traefik
