/**
 * Created by laura on 19/07/2016.
 */
// For quick access to those namespaces:
var FOAF = $rdf.Namespace('http://xmlns.com/foaf/0.1/');
var RDF = $rdf.Namespace('http://www.w3.org/1999/02/22-rdf-syntax-ns#');
var RDFS = $rdf.Namespace("http://www.w3.org/2000/01/rdf-schema#");
var XSD = $rdf.Namespace("http://www.w3.org/TR/2004/REC-xmlschema-2-20041028/#dt-");
var PROV = $rdf.Namespace('http://www.w3.org/ns/prov#');
var PROMS = $rdf.Namespace('http://promsns.org/def/proms#');


// Build Person
function Person(label, uri, givenName, familyName, mbox) {
    this.label = label;
    this.givenName = givenName;
    this.familyName = familyName;
    this.mbox = mbox;
    if (uri) {
        this.uri = uri;
    }
    // TODO: Fix up the uri
    else {
        this.uri = 'http://placeholder.org#';
    }

    this.makeGraph = function () {
        this.g = new $rdf.graph();
        //this.g.add($rdf.sym(this.uri), RDF('type'), PROV('Person')); -- redundant
        this.g.add($rdf.sym(this.uri), RDF('type'), PROV('Person'));

        this.g.add($rdf.sym(this.uri), FOAF('familyName'), this.familyName);
        this.g.add($rdf.sym(this.uri), FOAF('givenName'), this.givenName);
        this.g.add($rdf.sym(this.uri), FOAF('mbox'), this.mbox);

        return this.g;
    };
    this.get_graph = function () {
        if (!this.g) {
            this.makeGraph();
            return this.g;
        }
    };
    this.serialize_graph = function() {
        var sg = this.get_graph();
        var triples = new $rdf.serialize(sg.toN3(sg));
        return triples;
     };
}


// Build ReportingSystem
function ReportingSystem(label, uri, comment, actedOnBehalfOf) {
    this.label = label;
    if (uri) {
        this.uri = uri;
    }
    // TODO: Fix up the uri
    else {
        this.uri = 'http://placeholder.org#';
    }
    if (comment) {
        this.comment = comment;
    }
    // if (name) this.name = name
    if (actedOnBehalfOf) {
        this.actedOnBehalfOf = actedOnBehalfOf;
    }

    this.makeGraph = function () {
        this.g = new $rdf.graph();

        //this.g.add($rdf.sym(this.uri), RDF('type'), OWL('Class')); -- redundant
        //this.g.add($rdf.sym(this.uri), RDF('type'), PROV('Person')); -- redundant
        this.g.add($rdf.sym(this.uri), RDF('type'), PROMS('ReportingSystem'));

        this.g.add($rdf.sym(this.uri), RDFS('label'), $rdf.lit(this.label, 'en', XSD('string')));
        this.g.add($rdf.sym(this.uri), RDFS('comment'), $rdf.lit(this.comment, 'en', XSD('string')));

        if (this.actedOnBehalfOf) {
            var ag = new $rdf.graph;
            ag = this.actedOnBehalfOf.get_graph();

            this.g.add($rdf.sym(this.uri), PROV('actedOnBehalfOf'), this.actedOnBehalfOf.uri);

            // HACK AROUND
            //this.g.add($rdf.sym(this.actedOnBehalfOf.uri), RDF('type'), PROV('Person')); -- redundant
            this.g.add($rdf.sym(this.actedOnBehalfOf.uri), RDF('type'), PROV('Person'));

            this.g.add($rdf.sym(this.actedOnBehalfOf.uri), FOAF('familyName'), this.actedOnBehalfOf.familyName);
            this.g.add($rdf.sym(this.actedOnBehalfOf.uri), FOAF('givenName'), this.actedOnBehalfOf.givenName);
            this.g.add($rdf.sym(this.actedOnBehalfOf.uri), FOAF('mbox'), this.actedOnBehalfOf.mbox);
        }
    };

    this.get_graph = function () {
        if (!this.g) {
            this.makeGraph();
            return this.g;
        }
    }
}

