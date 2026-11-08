FROM php:8.2-cli-bookworm
RUN apt-get update && apt-get install -y --no-install-recommends python3 git unzip \
    && rm -rf /var/lib/apt/lists/* && useradd -r -u 10001 lab
COPY --from=composer:2 /usr/bin/composer /usr/bin/composer
WORKDIR /app
RUN composer require --no-interaction --no-progress --prefer-dist 'monolog/monolog:2.3.0' \
    && git clone --depth 1 https://github.com/ambionics/phpggc.git /opt/phpggc
COPY php-unserialize/index.php /app/index.php
COPY php-unserialize/generate.php /app/generate.php
COPY web/server.py /app/server.py
ENV APP_NAME="PHP / unserialize" LAB_COMMAND="php /app/index.php"
USER lab
EXPOSE 8080
CMD ["python3", "-u", "/app/server.py"]
