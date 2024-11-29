from setuptools import setup, find_packages

setup(name="content_check",
      version='0.0.1',
      packages=['api/v1/endpoints','services','api', 'models','api/v1', 'models/engine', 'api/v1/endpoints/chec_consent', 'services','avro_schemas_registry'
                ])
