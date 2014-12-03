#coding: utf-8
from elasticsearch import Elasticsearch


class ICitation(object):


    def __init__(self, hosts=None, **kwargs):
        """
        On class initialization is created a connection to ES and
        verify if is up with citation index, raise except otherwise.

        :param hosts: list of nodes we should connect
        :param kwargs: elasticsearch params, see:
        http://elasticsearch-py.readthedocs.org/en/master/api.html#elasticsearch.Elasticsearch
        """

        self.index = "citations"
        self.es_conn = Elasticsearch(hosts, **kwargs)

        if not self._ping():
            raise Exception("The Elasticsearch is down!")

        if not self._exists():
            raise Exception("The Elasticsearch dont have index 'citations'")


    def _ping(self):
        """
        :returns: Boolean ``True`` if ES is up, ``False`` otherwise
        """
        return bool(self.es_conn.ping())


    def _exists(self):
        """
        Verify if the citation index exists.

        :returns: Boolean ``True`` if exists or ``False`` otherwise.
        """
        return bool(self.es_conn.indices.exists(index=self.index))


    def count_citation(self):
        """
        Count the total of citation in citation index.

        :returns: Interger.
        """
        return int(self.es_conn.count(index=self.index)['count'])


    def get_all(self, size=1000):
        """
        Get all citation in citation index.

        :param size: Number of hits to return (default: 1000).

        :returns: A generator with citation data structure.
        """
        from_ = 0

        while True:

            resp = self.es_conn.search(index=self.index, from_=from_,
                                       size=size, body={"query": {"match_all": {}}})

            for citation in resp['hits']['hits']:
                yield citation

            from_ += size

            if from_ > resp['hits']['total']:
                raise StopIteration


    def get_identifiers(self):
        """
        Get all identifiers in index citation.

        :returns: a list content tuple, like: ('acronym of collection', SciELO PID).
        """
        all_citations = self.get_all()

        return [(i['_source']['collection'],i['_source']['code'])
                for i in all_citations]


    def index_citation(self, doc):
        """
        Index article and validate if have some attributes.

        :param doc: a dictionary that must have two keys ``code`` and
        ``collection``, must be a dicionary.

        :returns:{
                  "_index":"citations",
                  "_type":"citation",
                  "_id":"gyhX6cfOQLiGoktJ8aDjFw",
                  "_version":1,
                  "created":true
                 } (Elasticsearch response)
        """

        if not isinstance(doc, dict):
            raise TypeError('param doc must be a dicionary!')

        if not 'code' or not 'collection' in doc:
            raise ValueError('param doc must contain keys code and collection')

        return self.es_conn.index(index=self.index, doc_type='citation', body=doc)


    def del_all_citation(self):
        """
        Delete all documents from index citations, try to delete index only if
        it exists in Elasticsearch.

        This method can returns a Elasticsearch response or None if the index
        doesnt exists.

        :returns:{
                 "_indices":
                    {"citations":
                        {"_shards":
                            {"successful": 5, "failed": 0, "total": 5}
                        }
                    }
                }
        """

        if self._exists():
            return self.es_conn.delete_by_query(index=self.index,
                                                body={"query": {"match_all": {}}})


    def del_citation(self, ident):
        """
        Remove citation by identifier, (u'S0898-9081938912378', u'scl').

        :returns:{
                 "_indices":
                    {"citations":
                        {"_shards":
                            {"successful": 5, "failed": 0, "total": 5}
                        }
                    }
                }
        """

        if self._exists():
            return self.es_conn.delete_by_query(index=self.index,
                body="""{
                          "query": {
                            "bool": {
                              "must": [
                                {"match_phrase": {"code": %s}},
                                {"match_phrase": {"collection": %s}}
                              ]
                            }
                          }
                        }""" % (str(ident[1]), str(ident[0])))
