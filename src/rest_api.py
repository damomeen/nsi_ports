import logging
from flask import Flask, jsonify
from flask.ext.autodoc import Autodoc
from port_retrieval import get_nsi_topology


app = Flask(__name__)
auto = Autodoc(app)

topology = {}

#~ import logging_tree
#~ logging_tree.printout()



@app.route("/nsi/domains")
@auto.doc()
def get_domains():
    """Get list of NSI domains registeres in NSI AG
        
    Returns:
        1. HTTP code 200 and JSON list of URN identifiers of NSI domains registered in NSI AG
                (eg.: ["urn:ogf:network:geant.net:2013:topology", "urn:ogf:network:heanet.ie:2013:topology"])
    """
    global topology
    topology = get_nsi_topology(app.config["dds_service"])
    return jsonify(topology.keys())



@app.route("/nsi/domains/<domain>")
@auto.doc()
def get_domain_ports(domain):
    """Get list of ports (Service Termination Points -STPs) in given NSI domain.
        
    Attributes:
        - domain_name: [string] URN identifier of of NSI domain 
                (eg.: 'urn:ogf:network:pionier.net.pl:2013:topology')
    
    Returns:
        1. HTTP code 200 and JSON list of URN identifiers of NSI ports in the domain
                (eg.: ["PORT_TO_PIONIER", "felix-ge-1-0-9'", "MDVPN__lab__port"])
    """
    #topology = get_nsi_topology(app.config["dds_service"])
    return jsonify(topology.get(domain, []))
    
    
    
@app.route("/nsi/domains-full")
@auto.doc()
def get_domains_full():
    """Get list of NSI domains and its ports.
        
    Returns:
        1. HTTP code 200 and JSON object of URN identifiers of URN identifiers domains and ports
                (eg.: {"pionier.net.pl": ["PORT_TO_PIONIER", "felix-ge-1-0-9", "host2"],
                        "heanet.ie":["HEAnet-HRB-port", "HEANET-gsn-epa-port"]})
    """
    global topology
    topology = get_nsi_topology(app.config["dds_service"])
    return jsonify(topology)
    
    
    
@app.route('/nsi/domains/doc')
@auto.doc()
def documentation():
    """Generates HTML documentation of exposed REST API"""
    return auto.html(title='NSI ports REST API documentation')