from setuptools import setup, find_packages

setup(name="m_client",
      version='0.0.1',
      packages=['api/v1/endpoints','services','api', 'models','api/v1', 'models/engine', 'api/v1/endpoints/enterprise', 'services','avro_schemas_registry'
                ])
