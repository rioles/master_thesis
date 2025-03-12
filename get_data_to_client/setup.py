from setuptools import setup, find_packages

setup(name="get_data",
      version='0.0.1',
      packages=['api/v1/endpoints','services','api','api/v1',  'api/v1/endpoints/provider', 'message_queu', 'services','avro_schemas_registry'
                ])
