from __future__ import unicode_literals, absolute_import

# Please note, this is considered legacy DYE configuration.

import os

project_name = "internewshid"

repo_type = "git"
repository = 'git@github.com:aptivate/internewshid.git'

project_type = "django"

local_deploy_dir = os.path.dirname(__file__)

local_vcs_root = os.path.abspath(os.path.join(local_deploy_dir, os.pardir))

relative_django_dir = os.path.join('django', 'website')
relative_django_settings_dir = relative_django_dir

relative_ve_dir = os.path.join(relative_django_dir, '.ve')

requirements_per_env = False
local_requirements_file = os.path.join(local_deploy_dir, 'pip_packages.txt')

test_cmd = ' manage.py test'

host_list = {
    'production':   ['lin-' + project_name + '.aptivate.org:48001'],
    'staging':      ['fen-vz-' + project_name + '-stage.fen.aptivate.org'],
    'dev_server':   ['fen-vz-' + project_name + '-dev.fen.aptivate.org']
}

default_branch = {
    'production':   'master',
    'staging':      'staging',
    'dev_server':   'develop'
}

server_home = '/var/django'

server_project_home = os.path.join(server_home, project_name)

webserver = 'apache'
