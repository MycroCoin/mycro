FROM nginx:1.15

# copy nginx config and replace variables
ARG FRONTEND_HOST
ARG API_HOST
ENV FRONTEND_HOST=$FRONTEND_HOST
ENV API_HOST=$API_HOST
COPY ./ops/configs/nginx-prod.conf.template /etc/nginx/conf.d/nginx-prod.conf.template
# DOLLAR env variable enables escaping dollar sign in template
RUN DOLLAR="$" envsubst < /etc/nginx/conf.d/nginx-prod.conf.template > /etc/nginx/conf.d/default.conf

# add certificates
COPY ops/certs /etc/nginx/certs


COPY ./ops/wait_for_it.sh .
