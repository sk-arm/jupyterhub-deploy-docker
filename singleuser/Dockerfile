ARG DOCKER_NOTEBOOK_IMAGE
FROM $DOCKER_NOTEBOOK_IMAGE
ARG JUPYTERHUB_VERSION
RUN python3 -m pip install --no-cache tensorflow pandas sklearn matplotlib
RUN python3 -m pip install --no-cache jupyterhub==$JUPYTERHUB_VERSION
ADD model_manager-0.0.1-py3-none-any.whl /tmp
RUN python3 -m pip install /tmp/model_manager-0.0.1-py3-none-any.whl
RUN mkdir -p /home/jovyan/.jupyter/custom
RUN echo "#ipython_notebook img { height: 22px; margin-top: 4px; }" > /home/jovyan/.jupyter/custom/custom.css
