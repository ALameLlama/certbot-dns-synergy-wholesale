# certbot-dns-synergy-wholesale (This is WIP)
A Synergy Wholesale DNS plugin for Cerbot to authenticate and retrieve Lets Encrypt certificates

# TODO Update better docs and docker file.

credentials.ini should look something like this, remember to whitelist the IP for the certbot trying to use the api.
```
dns_synergy_wholesale_reseller_id = 1
dns_synergy_wholesale_api_key = abc123
```

basic usage:
```
certbot certonly \
  --authenticator dns-synergy-wholesale \
  --dns-synergy-wholesale-credentials /path/to/credentials.ini \
  -d 'example.com' \
  -d '*.example.com' \
```
