from haystack.backends import BaseEngine
import elasticsearch


# This is a hack to get around the fact that the Elasticsearch7SearchBackend requires elasticsearch < 8.0.0
original_version = elasticsearch.__version__
elasticsearch.__version__ = (7, 10 , 2)
try:
    from haystack.backends.elasticsearch7_backend import Elasticsearch7SearchBackend, Elasticsearch7SearchQuery
finally:
    elasticsearch.__version__ = original_version

class Elasticsearch8SearchBackend(Elasticsearch7SearchBackend):
    def __init__(self, connection_alias, **connection_options):
        super().__init__(connection_alias, **connection_options)

class Elasticsearch8SearchQuery(Elasticsearch7SearchQuery):
    def add_field_facet(self, field, **options):
        self.facets[field] = options.copy()

class Elasticsearch8SearchEngine(BaseEngine):
    backend = Elasticsearch8SearchBackend
    query = Elasticsearch8SearchQuery
