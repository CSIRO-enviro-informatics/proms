__author__ = 'django'
from rdflib import Graph, term
import re
import hashlib

def make_authorititive_serialisation_of_graph(g, named_graph_uri):
    """
    Serialises an RDF graph determanistically so it can be hashed.
    :return:
    """

    # serialise the graph as n-triples, remove trailing blank lines
    n_triples = g.serialize(format='nt').strip()

    # rename all the blank nodes
    n_triples = rename_blank_nodes(n_triples, create_bn_name_mapping(g))

    # form the n-triples into n-quads
    n_quads = form_ntriples_into_nquads(n_triples, named_graph_uri)

    # sort the n-quads by line alphabetically
    n_quads = '\n'.join(sorted(n_quads.splitlines()))

    return n_quads

# rename all the blank nodes in a n-triples serialisation of an RDF graph
def rename_blank_nodes(n_triples, bn_name_mapping):
    return multiple_replace(n_triples, bn_name_mapping)

# replace multiple strings within a string, with <before> & <after> terms specified by a dict
def multiple_replace(text, dict_of_pairs):
    if len(dict_of_pairs) > 0:
        rx = re.compile('|'.join(map(re.escape, dict_of_pairs)))
        def one_xlat(match):
            return dict_of_pairs[match.group(0)]
        return rx.sub(one_xlat, text)
    else:
        return text

# convert an n-triples serialisation of a graph into an n-quads serialisation by adding the named graph URI
def form_ntriples_into_nquads(n_triples, named_graph_uri):
    # split the n-triples string into lines
    g_array = n_triples.splitlines()

    # for each line, strip full stop, add the graph uri, re-add full stop
    for i in range(len(g_array)):
        g_array[i] = g_array[i].rstrip('.') + '<' + named_graph_uri + '> .'

    # return as a single string of n-quads
    return '\n'.join(g_array)

# map each blank node ID in a graph, however named, to a new ID of the form bn000001, bn000002, ... bn00000n
def create_bn_name_mapping(g):
    # find all the triples with blank node subjects
    bn_triples = []
    for s, p, o in g:
        if type(o) == term.BNode:  # we cna affort to find only those rows with the object as a BN for, given the
                                   # constraints of a PROMS Report, all BNs must be the object of some other triple
            bn_triples.append([str(s), str(p), str(o)])

    # order the BN triple lines alphabetically by predicate, then object, NOT by BN id
    bn_triples.sort()  # note the s p o -> p o s switch occurs above in array append

    # extract out the BNs now ordered by p then o, deduplicate the list keeping first seen occurrences
    bnids = []
    for triple in bn_triples:
        bnids.append(triple[2])
    bnids = dedupe(bnids)

    # create a BN renaming mapping and re-label them with IDs of the form bn000001, bn000002, ... bn00000n
    bn_mapping = {}
    i = 1
    for bnid in bnids:
        bn_mapping[bnid] = 'bn' + str(i).zfill(6)
        i += 1

    return bn_mapping

# deduplicate a list keeping the first seen occurence
def dedupe(seq):
    seen = set()
    seen_add = seen.add
    return [x for x in seq if not (x in seen or seen_add(x))]