# Legacy Mono 6.12 is built on Debian 10 (Buster), whose regular apt mirrors
# no longer serve package indexes. Use Debian's archived repositories for this
# intentionally vulnerable, localhost-only training image.
FROM mono:6.12

# Use the archived Debian 10 repositories; do not put Dockerfile RUN
# directives or shell comments inside a backslash-continued RUN instruction.
RUN set -eux; \
    printf '%s\n' \
      'deb http://archive.debian.org/debian buster main' \
      'deb http://archive.debian.org/debian-security buster/updates main' \
      > /etc/apt/sources.list; \
    find /etc/apt/sources.list.d -type f -name '*.list' \
      ! -iname '*mono*' -delete; \
    apt-get -o Acquire::Check-Valid-Until=false update; \
    apt-get install -y --no-install-recommends python3; \
    rm -rf /var/lib/apt/lists/*; \
    useradd -r -u 10001 lab

WORKDIR /app
COPY dotnet-binaryformatter/Program.cs ./Program.cs
RUN mcs -out:DeserLab.exe Program.cs
COPY web/server.py /app/server.py
ENV APP_NAME=".NET / BinaryFormatter (Mono)" LAB_COMMAND="mono /app/DeserLab.exe"
USER lab
EXPOSE 8080
CMD ["python3", "-u", "/app/server.py"]
