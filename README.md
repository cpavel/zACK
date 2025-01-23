zACK - Inbound Marketing Tool

Overview
zACK is an advanced inbound marketing tool designed to automate the process of lead generation and qualification for businesses seeking to enhance their online presence. The tool leverages the power of large language models (LLMs) like ChatGPT or other custom model to streamline the workflow of finding and qualifying leads from various online social media platforms, including Twitter, LinkedIn, and Hacker News. zACK is poised to revolutionize the way businesses approach online lead generation, providing a robust, automated solution that maximizes efficiency and effectiveness in identifying and engaging with potential leads.

Objectives
The primary goal of zACK is to automate the manual and often cumbersome process of online lead generation. By integrating with platform-specific search engines, zACK aims to filter and analyze content efficiently, reducing the need for manual intervention and allowing businesses to focus on high-quality leads.

Key Features
1. Automated Search and Collection: zACK regularly performs searches on platforms like Twitter, LinkedIn, and Hacker News using predefined keywords. This automation helps in managing the vast amount of data generated by these platforms.

2. Lead Qualification via LLMs: After collecting data, zACK uses ChatGPT or a custom LLM configured to qualify leads. The system applies specific prompts to determine the relevance and potential of each lead, asking binary questions to streamline the qualification process.

3. Response Generation: Once a lead is qualified, zACK generates tailored responses using additional prompts. This ensures that the communication aligns with the marketing objectives of the business.

4. Multi-User Support: zACK supports multiple users, each running distinct inbound marketing pipelines. For instance, user Pavel focuses on leads related to AI model training expenses, while user Dimitri targets Python contract opportunities.


## How to Start Everything

Assuming everything is installed and the `.env` file is configured properly, you can start the entire system (Redis, Celery, and Django server) with a single command:

```bash
./opt/zACK/bin/start_services.sh
```

This script will:
- Start the Redis server.
- Start the Celery worker.
- Start the Django server on `127.0.0.1:8000`. Use your DNS provider to map public IP address of the server to a URL of your choosing.

## System Requirements

- **OS**: Ubuntu 22.04 LTS
- **Python**: 3.11.x
- **Postgres**: 15.2 or greater
- **Redis**: 7.0.8 or greater

Libraries and dependencies: see `bin/apt_install`
Python packages: see `bin/pip_install`

## Installation and Configuration
Project Architecture in visual form: https://gitdiagram.com/cpavel/zACK

### Set Up Project (All Environments)

1. Rename `.env_` to `.env` and set up variables.
2. DB_ variables must be set for production or non-virtual environments. For Docker, it is defined in the ENV settings of the Dockerfile.
3. `RUNNING_ENVIRONMENT` is defined in the Dockerfile too (TODO: make Docker work in both dev and prod modes).
4. Obtain `OPENAI_KEY` from OpenAI or use your custom LLM API
5. The Django secret key can be recreated if necessary.

### Deployment Steps

1. SSH to the deployed server with the username and associated password:

   ```bash
   ssh username@server_IP
   ```

2. Download the project:

   ```bash
   sudo mkdir -p /opt/zACK
   ```

3. Perform a fresh installation:

   ```bash
   sudo git clone https://github.com/cpavel/zACK.git /opt/zACK
   sudo chown -R username:username /opt/zACK
   sudo chmod -R 755 /opt/zACK
   sudo ./opt/zACK/bin/apt_install
   sudo -u postgres psql
   CREATE DATABASE zackdb;
   CREATE USER admin WITH PASSWORD 'admin';
   GRANT ALL PRIVILEGES ON DATABASE zackdb TO admin;
   \q
   ```

Rename .env_ to .env and set up variables

   ```bash
   cd /opt/zACK
   sudo python3 -m venv venv
   source venv/bin/activate
   sudo chown -R username:username /opt/zACK/venv
   sudo chmod -R 755 /opt/zACK/venv
   pip install --upgrade pip
   pip install -q -r requirements.txt
   python manage.py makemigrations
   python manage.py migrate
   python manage.py createsuperuser
   ```

4. Run any DB migrations:

   ```bash
   python manage.py migrate
   ```

### Production Use

1. Create a superuser account using the Django helper (for admin):

   ```bash
   python manage.py createsuperuser
   ```

2. Log in to the account at the www.Your_URL.com/admin).
3. Create your search terms, prompt templates, and evaluation templates. See the ones already there for examples.

### Host Installation

- Rename `.env_` to `.env` and set up variables.
- Run `/bin/install`.

### Dev Tooling

- Black version 23.3.0 or greater

### Testing

- Use pytest. There is a helper executable in `./bin/run` for fast control. Consider aliasing it for faster development.

### Prod Setup

#### Nginx Set Up and Run

For Nginx to get access to the static files:

```bash
sudo usermod -a -G ack www-data
sudo chown -R :www-data /home/ack/ack/static
```

In the Nginx file (e.g., `/etc/nginx/sites-enabled/default`) add:

```bash
sudo vim /etc/nginx/sites-available/zack

server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    # Error handling (optional)
    error_page 500 502 503 504 /50x.html;
    location = /50x.html {
        root /usr/share/nginx/html;
    }
}

sudo ln -s /etc/nginx/sites-available/zack /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Docker Installation

Use Docker Compose to build and run the environment:

- Run `docker-compose build` from the ACK (repository) root folder.
- Run `docker-compose up`, it will run the container with the DEV environment and map the ACK folder to the container `/app` volume.

## Upcoming Dev Tooling

Some sort of type enforcer and some sort of linter. Options include either:

- [Ruff](https://github.com/charliermarsh/ruff) on its own.

Or a combination of:

- mypy
- flake8
- pylint

Ruff is new and exciting but needs to test claims. Current typing in the project is not enforced or complete.
