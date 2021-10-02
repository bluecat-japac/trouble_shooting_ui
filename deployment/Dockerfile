FROM <gateway-image>
USER root

ENV PERMISSION_PATH          "./workflows/trouble_shooting_ui/deployment/permissions.json"
ENV CONFIG_PATH              "./workflows/trouble_shooting_ui/deployment/config.py"

# Copy workflows to gateway
COPY  --chown=flask:root    ./workflows                   /builtin/workflows/
COPY  --chown=flask:root    ${CONFIG_PATH}                /builtin
COPY  --chown=flask:root    ${PERMISSION_PATH}            /builtin

RUN chmod +x /builtin/config.py

RUN if [ -s "/builtin/workflows/trouble_shooting_ui/requirements.txt" ]; then \
       pip3 install -r "/builtin/workflows/trouble_shooting_ui/requirements.txt"; \
    fi && \
    echo DONE

USER flask