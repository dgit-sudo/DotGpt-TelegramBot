# Deployment Guide for DotGPT Shop Bot

## Local Development Setup

### Prerequisites
- Python 3.9+
- Git
- pip package manager

### Quick Start (5 minutes)

1. **Clone and Setup**
```bash
git clone https://github.com/dgit-sudo/DotGpt-TelegramBot.git
cd DotGpt-TelegramBot
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2. **Get Your Bot Token**
   - Chat with [@BotFather](https://t.me/botfather) on Telegram
   - Use `/newbot` command
   - Follow instructions to create your bot
   - Copy the token

3. **Configure Environment**
```bash
cp .env.example .env
```

Edit `.env` with:
```
BOT_TOKEN=your_token_from_botfather
ADMIN_IDS=your_telegram_id
```

Find your Telegram ID by:
- Start [@userinfobot](https://t.me/userinfobot)
- It will show your user ID

4. **Initialize Database & Sample Data**
```bash
python init_sample_data.py
```

5. **Run the Bot**
```bash
python main.py
```

Your bot is now running! Send `/start` to it in Telegram.

---

## Production Deployment

### Option 1: VPS/Cloud Server (Recommended)

#### Using Ubuntu 20.04+ or Debian

1. **Connect to Server**
```bash
ssh user@your_server_ip
```

2. **Install Dependencies**
```bash
sudo apt update
sudo apt install python3.9 python3.9-venv python3-pip git postgresql postgresql-contrib
```

3. **Clone Repository**
```bash
cd /opt
sudo git clone https://github.com/dgit-sudo/DotGpt-TelegramBot.git
sudo chown -R $USER:$USER DotGpt-TelegramBot
cd DotGpt-TelegramBot
```

4. **Setup Virtual Environment**
```bash
python3.9 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

5. **Configure PostgreSQL Database**
```bash
sudo -u postgres psql
```

```sql
CREATE DATABASE dotgpt_db;
CREATE USER dotgpt_user WITH ENCRYPTED PASSWORD 'strong_password_here';
ALTER ROLE dotgpt_user SET client_encoding TO 'utf8';
ALTER ROLE dotgpt_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE dotgpt_user SET default_transaction_deferrable TO on;
ALTER ROLE dotgpt_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE dotgpt_db TO dotgpt_user;
\q
```

6. **Setup Environment File**
```bash
cp .env.example .env
nano .env
```

Update with:
```
BOT_TOKEN=your_actual_token
ADMIN_IDS=your_id
DATABASE_URL=postgresql://dotgpt_user:strong_password_here@localhost:5432/dotgpt_db
```

7. **Initialize Database**
```bash
source venv/bin/activate
python init_sample_data.py
```

8. **Create Systemd Service**
```bash
sudo nano /etc/systemd/system/dotgpt-bot.service
```

Add:
```ini
[Unit]
Description=DotGPT Shop Telegram Bot
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/opt/DotGpt-TelegramBot
Environment="PATH=/opt/DotGpt-TelegramBot/venv/bin"
ExecStart=/opt/DotGpt-TelegramBot/venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

9. **Start Service**
```bash
sudo systemctl daemon-reload
sudo systemctl enable dotgpt-bot
sudo systemctl start dotgpt-bot
```

10. **Check Status**
```bash
sudo systemctl status dotgpt-bot
sudo journalctl -u dotgpt-bot -f  # View logs
```

---

### Option 2: Docker Deployment

#### Dockerfile
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main.py"]
```

#### Build and Run
```bash
docker build -t dotgpt-bot .
docker run -d --name dotgpt --env-file .env dotgpt-bot
```

#### Docker Compose
Create `docker-compose.yml`:
```yaml
version: '3.8'

services:
  db:
    image: postgres:14
    environment:
      POSTGRES_DB: dotgpt_db
      POSTGRES_USER: dotgpt_user
      POSTGRES_PASSWORD: strong_password
    volumes:
      - postgres_data:/var/lib/postgresql/data

  bot:
    build: .
    environment:
      BOT_TOKEN: ${BOT_TOKEN}
      ADMIN_IDS: ${ADMIN_IDS}
      DATABASE_URL: postgresql://dotgpt_user:strong_password@db:5432/dotgpt_db
    depends_on:
      - db
    restart: always

volumes:
  postgres_data:
```

Run with:
```bash
docker-compose up -d
```

---

### Option 3: PaaS Deployment (Heroku)

#### Create Procfile
```
web: python main.py
```

#### Create Buildpacks
```bash
heroku create dotgpt-bot
heroku buildpacks:add heroku/python

heroku config:set BOT_TOKEN=your_token
heroku config:set ADMIN_IDS=your_id
heroku addons:create heroku-postgresql:hobby-dev

git push heroku main
```

---

## Monitoring & Maintenance

### Check Bot Status
```bash
# If using systemd:
sudo systemctl status dotgpt-bot

# If using Docker:
docker ps | grep dotgpt
docker logs dotgpt-bot

# Check logs
tail -f /opt/DotGpt-TelegramBot/bot.log
```

### Backup Database
```bash
# PostgreSQL backup
pg_dump -U dotgpt_user -h localhost dotgpt_db > backup_$(date +%Y%m%d).sql

# SQLite backup
cp dotgpt_bot.db dotgpt_bot_$(date +%Y%m%d).db.backup
```

### Update Bot
```bash
cd /opt/DotGpt-TelegramBot
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart dotgpt-bot
```

---

## Troubleshooting

### Bot not responding
1. Check bot token is correct
2. Verify bot has webhook/polling enabled
3. Check logs: `sudo journalctl -u dotgpt-bot -n 50`

### Database connection errors
1. Verify DATABASE_URL in .env
2. Check PostgreSQL is running: `sudo systemctl status postgresql`
3. Test connection: `psql postgresql://user:pass@localhost/db`

### High memory usage
- Implement pagination better
- Clear old messages periodically
- Use database connection pooling

---

## Performance Tips

1. **Database Indexes**: Add indexes for frequently queried fields
2. **Caching**: Consider Redis for session data
3. **Load Balancing**: Use multiple bot instances with webhook
4. **Database Optimization**: Regular `VACUUM` and `ANALYZE` on PostgreSQL

---

## SSL/HTTPS Setup (Recommended for Production)

For webhook deployment instead of polling:

```bash
# Get Let's Encrypt certificate
sudo apt install certbot
sudo certbot certonly --standalone -d yourdomain.com

# Update bot to use webhook
# See telegram.ext documentation for webhook setup
```

---

## Support & Resources

- [Telegram Bot API](https://core.telegram.org/bots/api)
- [python-telegram-bot Documentation](https://python-telegram-bot.readthedocs.io/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

