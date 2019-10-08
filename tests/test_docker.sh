#!/bin/sh
# this is a very simple script that tests the docker configuration for cookiecutter-django
# it is meant to be run from the root directory of the repository, eg:
# sh tests/test_docker.sh

export LAUNCHR_POSTGRES_USER="postgresuser-test"
export LAUNCHR_CELERY_FLOWER_USER="floweruser-test"
export LAUNCHR_CELERY_FLOWER_PASSWORD="celeryflowerpassword-test"
export LAUNCHR_POSTGRES_PASSWORD="postgrespassword-test"
export LAUNCHR_DJANGO_ADMIN_URL="adminurl-test"
export LAUNCHR_DJANGO_SECRET_KEY="secretkey-test"

set -o errexit

# install test requirements
pip3 install -r requirements.txt

# create a cache directory
mkdir -p .cache/docker
cd .cache/docker

# create the project using the default settings in cookiecutter.json
cookiecutter ../../ --no-input --overwrite-if-exists project_name=launchr_docker_test $@
cd launchr_docker_test

docker-compose -f local.yml build

# run the project's type checks
docker-compose -f local.yml run django mypy launchr_docker_test

# Run flake8
docker-compose -f local.yml run django flake8

# run the project's tests
docker-compose -f local.yml run django pytest --cov --cov-report xml
sed -i.bak "s;launchr_docker_test/;{{cookiecutter.project_slug}}/{{cookiecutter.project_slug}}/;g" coverage.xml
sed -i.bak "s;launchr_docker_test/;{{cookiecutter.project_slug}}/{{cookiecutter.project_slug}}/;g" .coverage
cp coverage.xml ../../../coverage.xml
cp .coverage ../../../.coverage

# return non-zero status code if there are migrations that have not been created
docker-compose -f local.yml run django python manage.py makemigrations --dry-run --check || { echo "ERROR: there were changes in the models, but migration listed above have not been created and are not saved in version control"; exit 1; }

# Test support for translations
docker-compose -f local.yml run django python manage.py makemessages

rm -rf .cache/docker
