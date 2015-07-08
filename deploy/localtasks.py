from __future__ import unicode_literals, absolute_import


def post_deploy(environment):
    """ This function is called by the main deploy in dye/tasklib after
    all the other tasks are done.  So this is the place where you can
    add any custom tasks that your project requires, such as creating
    directories, setting permissions etc."""
    dummy_task()


def dummy_task():
    """You can create many tasks callable individually, or just by
    post_deploy"""
    pass


def run_jenkins():
    """
    Make sure the local settings is correct and the database exists.
    Override the one in tasklib to load fixtures after all tables are created.
    """
    from dye.tasklib.environment import env
    env['verbose'] = True

    # don't want any stray .pyc files causing trouble
    from dye.tasklib import tasklib, deploy
    tasklib._rm_all_pyc()
    tasklib._install_django_jenkins()
    deploy('jenkins')

    test_args = ['--tb=short', '--create-db',
        # Remove all coverage options while pytest-cov is not installed.
        # '--cov-config=jenkins/coverage.rc',
        # '--cov=django/website/',
        # '--cov-report=xml',
        '--junitxml=junit.xml']

    tasklib._manage_py(['test'] + test_args)
