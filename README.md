PROMS Server
============
PROMS Server is an application designed to manage provenance information sent from a series of "reporting systems" which map their processes to a constraned variant of the [PROV Data Model](https://www.w3.org/TR/prov-dm/). It consists of a RESTful API (Python Flask) that both enforces data policy for incoming provenance information and also makes that information available in several ways. 

PROMS Server works as an application layer on top of an RDF triplestore (graph database) and required a web server, such as Apache, to broker access to it online.

For pretty much everything you need to know about PROMS Server and the family of tools associated with it, see http://promsns.org/wiki/proms.


PROMS Server is jointly maintained by [CSIRO](http://www.csiro.au) and [Geoscience Australia](http://www.ga.gov.au).