ARG VERSION=v5.0.0
FROM certbot/certbot:$VERSION

LABEL org.opencontainers.image.source="https://github.com/ALameLlama/certbot-dns-synergy-wholesale"
LABEL maintainer="nicholas@ciech.anow.ski"
ENV PYTHONIOENCODING="UTF-8"

RUN apk add --no-cache git

COPY . src/certbot-dns-synergy-wholesale

RUN pip install -U pip
RUN pip install --no-cache-dir src/certbot-dns-synergy-wholesale

ENTRYPOINT ["/usr/bin/env"]
