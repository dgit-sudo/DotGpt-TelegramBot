# Deployment Guide for E-commerce Telegram Bot

## Quick Start (Local Development)

1. **Install Python 3.8+**
   ```bash
   python --version  # Should be 3.8 or higher
   ```

2. **Clone and Setup**
   ```bash
   git clone https://github.com/dgit-sudo/DotGpt-TelegramBot.git
   cd DotGpt-TelegramBot
   pip install -r requirements.txt
   ```

3. **Configure Bot**
   ```bash
   cp .env.example .env
   # Edit .env with your bot token and admin user ID
   ```

4. **Run Setup Check**
   ```bash
   python setup.py
   ```

5. **Start Bot**
   ```bash
   python bot.py
   ```

## Production Deployment

### Option 1: Virtual Private Server (VPS)

#### Using systemd (Recommended for Linux)

1. **Create a service file**:
   ```bash
   sudo nano /etc/systemd/system/telegram-bot.service
   ```

2. **Add the following content**:
   ```ini
   [Unit]
   Description=E-commerce Telegram Bot
   After=network.target

   [Service]
   Type=simple
   User=youruser
   WorkingDirectory=/path/to/DotGpt-TelegramBot
   ExecStart=/usr/bin/python3 /path/to/DotGpt-TelegramBot/bot.py
   Restart=always
   RestartSec=10

   [Install]
   WantedBy=multi-user.target
   ```

3. **Enable and start the service**:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable telegram-bot
   sudo systemctl start telegram-bot
   sudo systemctl status telegram-bot
   ```

4. **View logs**:
   ```bash
   sudo journalctl -u telegram-bot -f
   ```

### Option 2: Docker Deployment

1. **Create Dockerfile**:
   ```dockerfile
   FROM python:3.11-slim

   WORKDIR /app

   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt

   COPY . .

   CMD ["python", "bot.py"]
   ```

2. **Create docker-compose.yml**:
   ```yaml
   version: '3.8'
   
   services:
     bot:
       build: .
       restart: unless-stopped
       volumes:
         - ./bot_database.db:/app/bot_database.db
       env_file:
         - .env
   ```

3. **Run with Docker Compose**:
   ```bash
   docker-compose up -d
   docker-compose logs -f
   ```

### Option 3: Cloud Platforms

#### Heroku

1. **Create Procfile**:
   ```
   worker: python bot.py
   ```

2. **Deploy**:
   ```bash
   heroku create your-bot-name
   heroku config:set TELEGRAM_BOT_TOKEN=your_token
   heroku config:set ADMIN_USER_ID=your_id
   git push heroku main
   ```

#### Railway.app

1. **Connect your GitHub repository**
2. **Add environment variables** in Railway dashboard
3. **Deploy automatically**

#### DigitalOcean App Platform

1. **Connect repository**
2. **Set as Worker** (not Web Service)
3. **Add environment variables**
4. **Deploy**

### Option 4: Using Screen (Simple VPS)

```bash
# Install screen
sudo apt install screen

# Start a new screen session
screen -S telegram-bot

# Run the bot
python bot.py

# Detach from screen (Ctrl+A, then D)
# Reattach later with: screen -r telegram-bot
```

## Database Backup

### Automatic Backup Script

Create `backup.sh`:
```bash
#!/bin/bash
BACKUP_DIR="backups"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR
cp bot_database.db "$BACKUP_DIR/bot_database_$DATE.db"
# Keep only last 7 backups
ls -t $BACKUP_DIR/bot_database_*.db | tail -n +8 | xargs rm -f
```

Add to crontab for daily backups:
```bash
crontab -e
# Add: 0 2 * * * /path/to/backup.sh
```

## Monitoring and Maintenance

### Health Check Script

Create `health_check.py`:
```python
import os
import sys
from datetime import datetime

def check_bot_running():
    """Check if bot process is running"""
    import psutil
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            cmdline = ' '.join(proc.info['cmdline'])
            if 'bot.py' in cmdline:
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    return False

if __name__ == '__main__':
    if check_bot_running():
        print(f"{datetime.now()}: Bot is running ✅")
    else:
        print(f"{datetime.now()}: Bot is NOT running ❌")
        sys.exit(1)
```

### Log Rotation

For production, configure log rotation in `/etc/logrotate.d/telegram-bot`:
```
/path/to/bot/logs/*.log {
    daily
    rotate 14
    compress
    delaycompress
    missingok
    notifempty
}
```

## Security Best Practices

1. **Never commit .env file** (already in .gitignore)
2. **Use strong passwords** for database if using PostgreSQL/MySQL
3. **Keep dependencies updated**:
   ```bash
   pip list --outdated
   pip install --upgrade -r requirements.txt
   ```
4. **Regular backups** of database
5. **Monitor logs** for suspicious activity
6. **Use HTTPS** if exposing any web interfaces
7. **Limit file permissions**:
   ```bash
   chmod 600 .env
   chmod 644 bot_database.db
   ```

## Scaling Considerations

### Using PostgreSQL (for high traffic)

1. **Install PostgreSQL**
2. **Update .env**:
   ```env
   DATABASE_URL=postgresql://user:password@localhost/botdb
   ```
3. **Install psycopg2**:
   ```bash
   pip install psycopg2-binary
   ```

### Load Balancing

For very high traffic, consider:
- Multiple bot instances with shared database
- Redis for caching user sessions
- Message queue for async processing

## Troubleshooting

### Bot stops unexpectedly
- Check logs: `sudo journalctl -u telegram-bot -f`
- Ensure enough memory: `free -h`
- Check disk space: `df -h`

### Database locked errors
- Use PostgreSQL instead of SQLite for production
- Or ensure only one bot instance is running

### Connection issues
- Check internet connection
- Verify bot token is correct
- Check Telegram API status

## Updates and Maintenance

```bash
# Pull latest changes
git pull origin main

# Update dependencies
pip install -r requirements.txt --upgrade

# Restart bot
sudo systemctl restart telegram-bot
```

## Support

For issues and questions:
- Open an issue on GitHub
- Check existing documentation
- Contact the administrator
