# Jobs statistics application for a supercomputer
The application gathers all information about running and finished jobs
and aggregated monitoring data from nodes.
It allows to display all tasks, to filter them basing on custom tagging mechanism,
to provide a detailed job report with monitoring data graphs,
to show a general jobs statistics bu runtime, length, resources and so on.

## Requirements
python3.5+, postrgresql, postgresql-devel

## Installation
`python3.5 -m venv venv`

`source venv/bin/activate`

`pip install -r requirements.txt`

later use `source venv/bin/activate` every time you want to work with the project

## Setup
If you want to use a default config, you must create postgresql user "user"
with password "password" and with access to databases: jd_testing, jd_development, jd_production.
Or use your custom settings and edit `config.py`

One time setup to create all tables:

for development:
`python init.py -c dev --drop`

for production:
`python init.py -c prod --drop`

## Testing
`python test.py`

## Starting
All application settings (host, port, db path, etc) are stored in `config.py`.
All service settings(cluster staff) are stored in `cluster_config/*.py`.

Running for development:
`python run.py -c dev`

Running for production:
`python run.py -c prod`

## License
Distributed under the MIT License - see the accompanying file LICENSE.
