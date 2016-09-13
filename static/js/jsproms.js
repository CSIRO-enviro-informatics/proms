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
var DC = $rdf.Namespace('http://purl.org/dc/elements/1.1/');
var DCAT = $rdf.Namespace('http://www.w3.org/n2/dcat#');


/*
    Build Person
*/
function Agent(label, uri, givenName, familyName, mbox) {
    this.label = label;
    this.givenName = givenName;
    this.familyName = familyName;
    this.mbox = mbox;
    if (uri) {
        this.uri = uri;
    }
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


/*
    Build Entity
*/

function Entity(label, uri, comment, wasAttributedTo, creator, created, licence, metadataUri, downloadURL) {
    this.label = label;
    if (uri) {
        this.uri = uri;
    }
    else {
        this.uri = 'http://placeholder.org#';
    }
    if (comment) {
        this.comment = comment;
    }
    if (wasAttributedTo) {
        this.wasAttributedTo = wasAttributedTo;
    }
    if (creator) {
        this.creator = creator;
    }
    if (created) {
        this.created = created;
    }
    if (licence) {
        this.licence = licence;
    }
    if (metadataUri) {
        this.metadataUri = metadataUri;
    }
    if (downloadURL) {
        this.downloadURL = downloadURL;
    }




    this.makeGraph = function() {

        this.g = new $rdf.graph();

        this.g.add($rdf.sym(this.uri), RDF('type'), PROV('Entity'));

        if (this.wasAttributedTo) {
            this.g.add($rdf.sym(this.uri), PROV('wasAttributedTo'), $rdf.sym(this.wasAttributedTo.uri));
        }

        if (this.creator) {
            this.g.add($rdf.sym(this.uri), PROV('creator'), $rdf.lit(this.creator.uri, 'en', XSD('anyUri')));
        }

        if (this.created) {
            this.g.add($rdf.sym(this.uri), DC('created'), $rdf.lit(this.created, 'en', XSD('dateTime')));
        }

        if (this.licence) {
            this.g.add($rdf.sym(this.uri), DC('licence'), $rdf.lit(this.licence, 'en', XSD('string')));
        }

        if (this.metadataUri) {
            this.g.add($rdf.sym(this.uri), PROMS('metadataUri'), $rdf.lit(this.metadataUri, 'en', XSD('anyUri')));
        }

        if (this.downloadURL) {
            this.g.add($rdf.sym(this.uri), DCAT('downloadURL'), $rdf.lit(this.downloadURL, 'en', XSD('anyUri')));
        }
    }

    this.get_graph() = function {
         if (!this.g) {
             this.makeGraph();
             return this.g;
         }
    }

}

/*
    Build Activity
*/

function Activity(label, startedAtTime, endedAtTime, uri, wasAssociatedWith, comment, used_entities, generated_entities, wasInformedBy, namedActivityUri) {

    this.label = label;

    this.startedAtTime = startedAtTime;
    this.endedAtTime = endedAtTime;

    if (uri) {
        this.uri = uri;
    }
    else {
        this.uri = 'http://placeholder.org#';
    }

    if (wasAssociatedWith) {
        this.wasAssociatedWith = wasAssociatedWith;
    }

    if (used_entities) {
        this.used_entities = used_entities;
    }

    if (generated_entities) {
        this.generated_entities = generated_entities;
    }

    if (wasInformedBy) {
        this.wasInformedBy = wasInformedBy;
    }

    this.makeGraph = function () {
        this.g = new $rdf.graph();

        this.g.add($rdf.sym(this.uri), RDF('type'), PROV('Activity'));

        this.g.add($rdf.sym(this.uri), PROV('startedAtTime'),$rdf.lit(this.startedAtTime, 'en', XSD('dateTime')) )
        this.g.add($rdf.sym(this.uri), PROV('endedAtTime'),$rdf.lit(this.endedAtTime, 'en', XSD('dateTime')) )

        if (this.wasAssociatedWith) {
            this.g.add($rdf.sym(this.uri), PROV('wasAssociatedWith'), $rdf.sym(this.wasAssociatedWith.uri));
        }

        if (this.used_entities) {
            for (var used_entity in used_entities) {
                // add entity to graph
                this.g.add(used_entity.get_graph());
                // associate entity with activity
                this.g.add($rdf.sym(this.uri), PROV('used'), $rdf.sym(used_entity.uri));
            }
        }

        if (this.generated_entities) {
            for (var generated_activity in generated_entities) {
                // add entity to graph
                this.g.add(generated_entities.get_graph());
                // associate entity with activity
                this.g.add($rdf.sym(this.uri), PROV('used'), $rdf.sym(generated_entities.uri));
            }
        }

        if (this.wasInformedBy) {
            this.g.add($rdf.sym(this.uri), PROV('wasInformedBy'),$rdf.sym(this.wasInformedBy.uri));
        }

    };


    this.get_graph = function () {
        if (!this.g) {
            this.makeGraph();
            return this.g;
        }
    }
}


/*
    Build ReportingSystem
*/

function ReportingSystem(label, uri, comment, actedOnBehalfOf) {
    this.label = label;
    if (uri) {
        this.uri = uri;
    }
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

        this.g.add($rdf.sym(this.uri), RDF('type'), PROMS('ReportingSystem'));

        this.g.add($rdf.sym(this.uri), RDFS('label'), $rdf.lit(this.label, 'en', XSD('string')));
        this.g.add($rdf.sym(this.uri), RDFS('comment'), $rdf.lit(this.comment, 'en', XSD('string')));

        if (this.actedOnBehalfOf) {
             // get graph of person, add it to this graph
            var ag = new $rdf.graph;
            ag = this.actedOnBehalfOf.get_graph();

            this.g.add($rdf.sym(this.uri), PROV('actedOnBehalfOf'), $rdf.sym(this.actedOnBehalfOf.uri));
            this.g.add(ag);

        }
    };

    this.get_graph = function () {
        if (!this.g) {
            this.makeGraph();
            return this.g;
        }
    }
}

/*
    Build Report
*/

function Report(label, reportingSystem, nativeId, reportActivity, comment, reportType) {

    this.label = label;
    this.uri = 'http://placeholder.org/reporting#';
    this.reportingSystem = reportingSystem;
    this.nativeId = nativeId;
    this.reportActivity = reportActivity;
    this.reportType = reportType;



    this.make_graph = function() {
        this.g = new $rdf.graph();

        if (this.reportType == "basic") {
            this.g.add($rdf.sym(this.uri), RDF('type'), PROMS('BasicReport'));
        }
        else if (this.reportType = "external") {
            this.g.add($rdf.sym(this.uri), RDF('type'), PROMS('ExternalReport'));
        }

        this.g.add(this.reportingSystem.get_graph());
        this.g.add($rdf.sym(this.uri), PROMS('reportinSystem'), $rdf.sym(this.reportingSystem.uri));

        this.g.add($rdf.sym(this.uri), PROMS('nativeId'),$rdf.lit(this.nativeId, 'en', XSD('string') )

        this.g.add(this.reportActivity.get_graph());
        this.g.add($rdf.sym(this.uri), PROMS('startingActivity'), $rdf.lit(this.reportActivity, 'en', XSD('string')));
        this.g.add($rdf.sym(this.uri), PROMS('endingActivity'), $rdf.lit(this.reportActivity, 'en', XSD('string')));

    }

    this.get_graph = function () {
        if (!this.g) {
            this.makeGraph();
            return this.g;
        }
    }

}