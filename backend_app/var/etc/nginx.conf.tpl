server {
    listen 8383;
    autoindex off;
    server_name myhears.patrowl.io localhost;

    root .;

    # access_log var/log/nginx.patrowlhears-access.log;
    # error_log var/log/nginx.patrowlhears-error.log;

    location / {
        proxy_pass http://127.0.0.1:8303;

        proxy_set_header X-Real-IP              $remote_addr;
        proxy_set_header X-Forwarded-For        $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Host       $host;
        proxy_set_header Proxy                  "";

        add_header 'Cache-Control' 'no-store, no-cache, must-revalidate, proxy-revalidate, max-age=0';
	      expires off;

        # Custom headers
        proxy_connect_timeout                   75s;
        proxy_read_timeout                      300s;

        proxy_redirect                          off;
        proxy_buffering                         off;
        proxy_buffer_size                       "4k";
    }

    location /static {
        alias __PH_INSTALL_DIR__/staticfiles;
    }
    location /media {
        alias __PH_INSTALL_DIR__/media;
    }
}

# server {
# 	listen 80 default_server;
# 	listen [::]:80 default_server;
# 	server_name _;
# 	return 301 https://$host$request_uri;
# }
#
# server {
#   listen 443 ssl;
#   autoindex on;
#
#   server_name localhost __PH_BASE_DOMAIN__;
#   ssl_certificate /etc/letsencrypt/live/__PH_BASE_DOMAIN__/fullchain.pem;
#   ssl_certificate_key /etc/letsencrypt/live/__PH_BASE_DOMAIN__/privkey.pem;
#   ssl_trusted_certificate /etc/letsencrypt/live/__PH_BASE_DOMAIN__/chain.pem;
#   include /etc/letsencrypt/options-ssl-nginx.conf; # managed by Certbot
#   ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem; # managed by Certbot
#
#   access_log /var/log/nginx.patrowlhears-access.ssl.log;
#   error_log  /var/log/nginx.patrowlhears-error.ssl.log;
#
#   location / {
#       proxy_pass http://localhost:8303;
#
#       proxy_set_header X-Real-IP              $remote_addr;
#       proxy_set_header X-Forwarded-For        $proxy_add_x_forwarded_for;
#       proxy_set_header X-Forwarded-Host       $host;
#       proxy_set_header Proxy                  "";
#
#       add_header 'Cache-Control' 'no-store, no-cache, must-revalidate, proxy-revalidate, max-age=0';
#       expires off;
#
#       proxy_ignore_client_abort               on;
#
#       # Custom headers
#       proxy_connect_timeout                   75s;
#       proxy_read_timeout                      300s;
#
#       proxy_redirect                          off;
#       proxy_buffering                         off;
#       proxy_buffer_size                       "4k";
#   }
#
#   location /static {
#       alias __PH_INSTALL_DIR__/staticfiles;
#   }
#   location /media {
#       alias __PH_INSTALL_DIR__/media;
#   }
#
# }
