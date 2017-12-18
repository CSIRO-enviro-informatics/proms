from lxml import etree
from lxml.builder import ElementMaker
import _database
import _config as conf
import urllib.parse as uriparse


# TODO: get_capabilities Python XML generation with an XML Jinja2 template
def get_capabilities():
    """This function enables an Open Geospatial Consortium Web Service-like GetCapabilities function which describes
    this service (PROMS as a whole) in a standardised way. See http://ogcnetwork.net/node/180 for the OGC's WFS
    GetCapabilities function description.

    This function is only called via the index page ('/')."""

    # TODO: add all API endpoints
    em = ElementMaker(
        namespace="http://fake.com/ldapi",
        nsmap={
            'ldapi': "http://fake.com/ldapi"
        }
    )
    onl = ElementMaker(
        namespace="http://fake.com/ldapi",
        nsmap={
            'xlink': "http://www.w3.org/1999/xlink",
        }
    )
    doc = em.LDAPI_Capabilities(
        em.Service(
            em.Name('PROMS Server'),
            em.Title('PRovenance Management System (PROMS) Server'),
            em.KeywordList(
                em.Keyword('provenance'),
                em.Keyword('RDF'),
                em.Keyword('Linked Data')
            ),
            # TODO: parameterised namespaces not working yet
            onl.OnlineResource(type="simple", href=conf.BASE_URI),
            em.ContactInformation(
                em.ContactPersonPrimary(
                    em.contactPerson('Nicholas Car'),
                    em.ContactOrganization('Geoscience Australia')
                ),
                em.ContactAddress(
                    em.AddressType('Postal'),
                    em.Address('GPO Box 378'),
                    em.City('Canberra'),
                    em.StateOrProvince('ACT'),
                    em.PostCode('2601'),
                    em.Country('Australia'),
                    em.ContactVoiceTelephone('+61 2 6249 9111'),
                    em.ContactFacsimileTelephone(),
                    em.ContactElectronicMailAddress('clientservices@ga.gov.au')
                )
            ),
            em.Fees('none'),
            em.AccessConstraints(
                '(c) Commonwealth of Australia (Geoscience Australia) 2016. This product is released under the ' +
                'Creative Commons Attribution 4.0 International Licence. ' +
                'http://creativecommons.org/licenses/by/4.0/legalcode'
            )
        ),
        em.Capability(
            em.Request(
                em.GetCapabilities(
                    em.Format('application/xml'),
                    em.DCPType(
                        em.HTTP(
                            em.Get(
                                onl.OnlineResource(
                                    type="simple",
                                    href=conf.BASE_URI +
                                         "?_view=getcapabilities&_format=application/xml"
                                ),
                            )
                        )
                    )
                ),
                em.Sample(
                    em.Format('text/html'),
                    em.Format('text/turtle'),
                    em.Format('application/rdf+xml'),
                    em.Format('application/rdf+json'),
                    em.DCPType(
                        em.HTTP(
                            em.Get(
                                onl.OnlineResource(
                                    type="simple",
                                    href=conf.BASE_URI + "object/{OBJECT_URI}"
                                ),
                            )
                        )
                    )
                )
            )
        )
    )
    return etree.tostring(
        doc,
        pretty_print=True,
        xml_declaration=True,
        encoding='UTF-8'
    )


def get_contents_classes():
    query = '''
            SELECT DISTINCT ?c
            WHERE {
                GRAPH ?g {
                    ?s a ?c .
                }
                FILTER(!REGEX(STR(?g), "/pingback/", "i")) .
            }
            ORDER BY ?c
    '''
    classes = []
    try:
        for c in _database.query(query)['results']['bindings']:
            classes.append({
                'uri': c['c']['value'],
                'uri_encoded': uriparse.quote_plus(c['c']['value'])
            })
    except ValueError:
        pass  # i.e. no result

    return classes
