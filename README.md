# certbot-dns-synergy-wholesale

<p align="center">
<a href="https://github.com/ALameLlama/certbot-dns-synergy-wholesale/actions/workflows/docker-publish.yml"><img src="https://img.shields.io/github/actions/workflow/status/ALameLlama/certbot-dns-synergy-wholesale/.github/workflows/docker-publish.yml" alt="Build"></a>
<a href="https://hub.docker.com/r/alamellama/certbot-dns-synergy-wholesale"><img alt="Docker Image Version" src="https://img.shields.io/docker/v/alamellama/certbot-dns-synergy-wholesale"></a>
<a href="https://hub.docker.com/r/alamellama/certbot-dns-synergy-wholesale"><img alt="Docker Pulls" src="https://img.shields.io/docker/pulls/alamellama/certbot-dns-synergy-wholesale"></a>
<a href="https://hub.docker.com/r/alamellama/certbot-dns-synergy-wholesale"><img alt="Docker Image Size (tag)" src="https://img.shields.io/docker/image-size/alamellama/certbot-dns-synergy-wholesale/latest"></a>
<a href="https://github.com/ALameLlama/certbot-dns-synergy-wholesale/blob/master/LICENSE"><img src="https://img.shields.io/badge/license-Apache%20License%202.0-blue.svg" alt="License"></a>
</p>

A [Synergy Wholesale](https://synergywholesale.com) DNS plugin for [Certbot](https://certbot.eff.org/) to authenticate and retrieve Lets Encrypt certificates. Automates the process of completing a `dns-01` challenge by creating, and subsequently removing, `TXT` records

## Installation

```
# create a virtual environment, to avoid conflicts
python3 -m venv /some/path

# activate the virtual environment
source /some/path/bin/activate

# use the pip in the virtual environment to install or update
/some/path/bin/pip install -U certbot-dns-synergy-wholesale

# use the cerbot from the virtualenv, to avoid accidentally
# using one from a different environment that does not have this library
/some/path/bin/certbot
```

## Named Arguments

To start using DNS authentication for Synergy Wholesale, pass the following arguments on certbot's command line:

| Option                                     | Description                                |
| ------------------------------------------ | ------------------------------------------ |
| `--authenticator dns-synergy-wholesale`    | select the authenticator plugin (Required) |
| `--dns-synergy-wholesale-credentials FILE` | credentials INI file. (Required)           |

## Credentials

Use of this plugin requires a configuration file containing API credentials, obtained from your [manage.synergywholesale.com](https://manage.synergywholesale.com/home/resellers/api).

**Warning:** You must whitelist the IP address from where certbot will run, Otherwise you'll run into API errors.

Remember this file will need to have 600 permissions.

An example `credentials.ini` file:

```{.sourceCode .ini}
dns_synergy_wholesale_reseller_id = 1
dns_synergy_wholesale_api_key = abc123
```

## Examples

To acquire a single certificate for both `example.com` and `*.example.com`

    certbot certonly \
      --authenticator dns-synergy-wholesale \
      --dns-synergy-wholesale-credentials /path/to/credentials.ini \
      -d 'example.com' \
      -d '*.example.com'

You can also add addtional paramaters such as `--keep-until-expiring --non-interactive --expand` for automation. More information [here](https://eff-certbot.readthedocs.io/en/stable/using.html#certbot-command-line-options)

## Docker

You can build a docker image from source using the included `Dockerfile` or pull the latest version directly from Docker Hub:

    docker pull alamellama/certbot-dns-synergy-wholesale

Once that's finished, the application can be run as follows:

    docker run --rm \
      -v /var/lib/letsencrypt:/var/lib/letsencrypt \
      -v /etc/letsencrypt:/etc/letsencrypt \
      --cap-drop=all \
      alamellama/certbot-dns-synergy-wholesale certbot certonly \
        --authenticator dns-synergy-wholesale \
        --dns-synergy-wholesale-credentials /var/lib/letsencrypt/credentials.ini \
        --keep-until-expiring --non-interactive --expand \
        --server https://acme-v02.api.letsencrypt.org/directory \
        --agree-tos --email "webmaster@example.com" \
        -d example.com -d '*.example.com'

You may want to change the volumes `/var/lib/letsencrypt` and `/etc/letsencrypt` to local directories where the certificates and configuration should be stored.

## Dev Setup

```
# Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install uv (if not already installed)
pip install uv

# Install all dependencies using the lockfile
uv sync --dev
```
