# Ack - The auto-tuning sales tool

## System requirements

OS: Ubuntu 23.04
Python: 3.11.1 or greater.
Postgres: 15.2 or greater.
Redis: 7.0.8 or greater.

Libraries: see bin/apt_install
Python: see bin/pip_install

There are also other helper executables in /bin for easy installation.

## Set up project (all env)

- Rename .env_ to .env and set up vars
- DB_ variables must be set for prod or non virtual env, for docker it is defined in ENV settings of dockerfile
- RUNNING_ENVIRONMENT is defined in dockerfile too (TODO: make dockers work in dev AND prod mode)
- OPENAI_KEY must be obtained from openapi
- DJANGO secret key can be recreated if necessary

## Local Docker installation

Use docker-compose to build and run environment:

- Run `docker-compose build` from ACK (repository) root folder
- Run `docker-compose up`, it will run container with DEV env and map ACK folder to container /app volume


## Deployment steps

There are no defined CI/CD pipelines to push changes from dev to production, you will have to ssh
to the deployed server with the user name and associated password:

```bash
ssh username@server_IP
```

Then run the following to download the project.

```bash
sudo mkdir -p /opt/zACK
```

To perform fresh installation, run:

```bash
sudo git clone https://github.com/cpavel/zACK.git /opt/zACK
sudo chown -R username:username /opt/zACK
sudo chmod -R 755 /opt/zACK
sudo ./opt/zACK/bin/apt_install
sudo python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip setuptools wheel
pip install -q -r requirements.txt
python manage.py runserver
```

To run any DB migrations, run:

```bash
python manage.py migrate
```

## Production Use
1. Create a superuser account using the django helper (for admin)
   `python manage.py createsuperuser`
2. Login to the account at the [admin](builtwithml.org/admin).
3. Create your search terms, prompt templates, and evalutation templates. See the ones already there for examples:

- Search terms are to execute search on HN through https://hn.algolia.com (try search terms there) and get comment+user profile of the author
- Search is limited for comments not older then 24h
- For each search result (and for each search term):
  - Get related prompt templates (i.e. - reach out message) and filter them by profile length)
  - Randomly select one  prompt template
  - Ask ChatGPT to reword prompt template using comment and user profile
  - Each prompt template has own evaluation template
  - For ChatGPT rewording response, ChatGPT is asked to evaluate score from 0 to 100 relavance based on evaluation template
  - if score < 60 (hardcoded), result is skipped, otherwise stored
  
- Requests to ChatGPT are limited by 10 (hardcoded), because of current OpenAPI account limitation (free account?)

4. Use Django Admin and Search Terms to initiate search and get rusults through actions

## Host Installation

Rename .env_ to .env and set up variables
Run /bin/install

## Dev tooling

Black version 23.3.0 or greater

## Testing

Use pytest. There is a helper exe in `./bin/run` for fast
control. Consider aliasing it for faster development.

## Prod setup

### Nginx set up and run
For nginx to get access to the static files:
```bash
sudo usermod -a -G ack www-data
sudo chown -R :www-data /home/ack/ack/static
```

In the nginx file (e.g., `/etc/nginx/sites-enabled/default`) add:

```bash
    echo 'server_name builtwithml.org;

    location / {
      # First attempt to serve request as file, then
      # as directory, then fall back to displaying a 404.
      proxy_pass http://127.0.0.1:8000;
      proxy_set_header Host $host;
      proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
      proxy_set_header X-Forwarded-Proto $scheme;
    }' | sudo tee /etc/nginx/sites-available/zACK

sudo ln -s /etc/nginx/sites-available/zACK /etc/nginx/sites-enabled/
```

Then run

```bash
sudo systemctl reload nginx
```

### Run Django Derver (first)
Run in deatached terminal `.bin/prod` (via screen for example)

### Run Celery (second)
Run in deatached terminal `.bin/celery` (via screen for example)

## Upcoming dev tooling

Some sort of type enforcer and some sort of linter. Options
include either:

[Ruff](https://github.com/charliermarsh/ruff) on it's own.

Or a combination of:

- mypy
- flake8
- pylint

Ruff is new and exciting but need to test claims. Current
typing in the project is not enforced or complete.
