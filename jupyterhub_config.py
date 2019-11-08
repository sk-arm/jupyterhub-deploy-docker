# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.

# Configuration file for JupyterHub
import os

c = get_config()

# We rely on environment variables to configure JupyterHub so that we
# avoid having to rebuild the JupyterHub container every time we change a
# configuration parameter.

c.JupyterHub.logo_file = '/opt/conda/share/jupyterhub/static/images/logo.svg'

# Spawn single-user servers as Docker containers
c.JupyterHub.spawner_class = 'dockerspawner.DockerSpawner'
# Spawn containers from this image
c.DockerSpawner.container_image = os.environ['DOCKER_NOTEBOOK_IMAGE']
# JupyterHub requires a single-user instance of the Notebook server, so we
# default to using the `start-singleuser.sh` script included in the
# jupyter/docker-stacks *-notebook images as the Docker run command when
# spawning containers.  Optionally, you can override the Docker run command
# using the DOCKER_SPAWN_CMD environment variable.
spawn_cmd = os.environ.get('DOCKER_SPAWN_CMD', "start-singleuser.sh")
c.DockerSpawner.extra_create_kwargs.update({ 'command': spawn_cmd })
# Connect containers to this Docker network
network_name = os.environ['DOCKER_NETWORK_NAME']
c.DockerSpawner.use_internal_ip = True
c.DockerSpawner.network_name = network_name
# Pass the network name as argument to spawned containers
c.DockerSpawner.extra_host_config = { 'network_mode': network_name }
# Explicitly set notebook directory because we'll be mounting a host volume to
# it.  Most jupyter/docker-stacks *-notebook images run the Notebook server as
# user `jovyan`, and set the notebook directory to `/home/jovyan/work`.
# We follow the same convention.
notebook_dir = os.environ.get('DOCKER_NOTEBOOK_DIR') or '/home/jovyan/work'
c.DockerSpawner.notebook_dir = notebook_dir
# Mount the real user's Docker volume on the host to the notebook user's
# notebook directory in the container
c.DockerSpawner.volumes = { 'jupyterhub-user-{username}': notebook_dir }
# volume_driver is no longer a keyword argument to create_container()
# c.DockerSpawner.extra_create_kwargs.update({ 'volume_driver': 'local' })
# Remove containers once they are stopped
c.DockerSpawner.remove_containers = True
# For debugging arguments passed to spawned containers
c.DockerSpawner.debug = True

c.DockerSpawner.options_form = """
        <div class="form-group">
            <label for="processorNumber" class="col-sm-6 col-form-label col-form-label-sm">Number Of Processors</label>
            <div class="col-sm-6" style="margin-bottom: 10px">
                <select id="processorNumber" name="processorNumber" class="form-control">
                    <option value="1">1</option>
                    <option value="2">2</option>
                    <option value="3" selected="1">3</option>
                </select>
            </div>
        </div>
        <div class="form-group">
            <label for="processorType" class="col-sm-6 col-form-label col-form-label-sm">Type Of Processor</label>
            <div class="col-sm-6" style="margin-bottom: 10px">
                <select id="processorType" name="processorType" class="form-control">
                    <option value="cpu">CPU</option>
                    <option value="gpu" selected="1">GPU</option>
                </select>
            </div>
        </div>
        <div class="form-group">
            <label for="ram" class="col-sm-6 col-form-label col-form-label-sm">RAM</label>
            <div class="col-sm-6" style="margin-bottom: 10px">
                <select id="ram" name="ram" class="form-control">
                    <option value="8gb">8 GB</option>
                    <option value="16gb" selected="1">16 GB</option>
                    <option value="32gb">32 GB</option>
                    <option value="64gb">64 GB</option>
                </select>
            </div>
        </div>
        <div class="form-group">
            <label for="storage" class="col-sm-6 col-form-label col-form-label-sm">Storage</label>
            <div class="col-sm-6" style="margin-bottom: 10px">
                <select id="storage" name="storage" class="form-control">
                    <option value="500gb" selected="1">500 GB</option>
                    <option value="1tb">1 TB</option>
                    <option value="2tb">2 TB</option>
                    <option value="4tb">4 TB</option>
                </select>
            </div>
        </div>
        """

# User containers will access hub by container name on the Docker network
c.JupyterHub.hub_ip = 'jupyterhub'
c.JupyterHub.hub_port = 8080

# TLS config
c.JupyterHub.port = 443
c.JupyterHub.ssl_key = os.environ['SSL_KEY']
c.JupyterHub.ssl_cert = os.environ['SSL_CERT']

# Authenticate users with GitHub OAuth

#c.JupyterHub.authenticator_class = 'oauthenticator.GitHubOAuthenticator'
#c.GitHubOAuthenticator.oauth_callback_url = os.environ['OAUTH_CALLBACK_URL']

c.JupyterHub.authenticator_class = 'dummyauthenticator.DummyAuthenticator'
c.DummyAuthenticator.password = "password"

# Persist hub data on volume mounted inside container
data_dir = os.environ.get('DATA_VOLUME_CONTAINER', '/data')

c.JupyterHub.cookie_secret_file = os.path.join(data_dir,
    'jupyterhub_cookie_secret')

c.JupyterHub.db_url = 'postgresql://postgres:{password}@{host}/{db}'.format(
    host=os.environ['POSTGRES_HOST'],
    password=os.environ['POSTGRES_PASSWORD'],
    db=os.environ['POSTGRES_DB'],
)

# Whitlelist users and admins
c.Authenticator.whitelist = whitelist = set()
c.Authenticator.admin_users = admin = set()
c.JupyterHub.admin_access = True
pwd = os.path.dirname(__file__)
with open(os.path.join(pwd, 'userlist')) as f:
    for line in f:
        if not line:
            continue
        parts = line.split()
        # in case of newline at the end of userlist file
        if len(parts) >= 1:
            name = parts[0]
            whitelist.add(name)
            if len(parts) > 1 and parts[1] == 'admin':
                admin.add(name)
