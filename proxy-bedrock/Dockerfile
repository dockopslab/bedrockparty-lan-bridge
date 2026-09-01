FROM python:3.13-alpine

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app
COPY bedrock-lan-proxy.py /app/bedrock-lan-proxy.py
COPY scripts/healthcheck-raknet.py /app/healthcheck-raknet.py
COPY licenses/BedrockParty-LICENSE /usr/share/licenses/bedrockparty/LICENSE

USER 65532:65532

EXPOSE 19132/udp

CMD ["python", "/app/bedrock-lan-proxy.py"]
