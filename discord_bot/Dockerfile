FROM python:3.14-slim
WORKDIR /app
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt
COPY __init__.py backend.py bot.py config.py store.py /app/discord_bot/
CMD ["python", "-m", "discord_bot.bot"]
