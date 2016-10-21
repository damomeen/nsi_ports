import logging, pickle, threading, urllib2
from multiprocessing.dummy import Pool
from flask import Flask, jsonify
from json import dumps
from flask.ext.autodoc import Autodoc
from port_retrieval import get_nsi_topology, parse_ports


app = Flask(__name__)
auto = Autodoc(app)

topology_lock = threading.Lock()

#~ import logging_tree
#~ logging_tree.printout()

TOPOLOGY_FILENAME = 'topology.pkl'


@app.route("/nsi/domains")
@auto.doc()
def get_domains():
    """Get list of NSI domains registeres in NSI AG
        
    Returns:
        1. HTTP code 200 and JSON list of URN identifiers of NSI domains registered in NSI AG
                (eg.: ["urn:ogf:network:geant.net:2013:topology", "urn:ogf:network:heanet.ie:2013:topology"])
    """  
    topology = get_nsi_topology(app.config["dds_service"])
    with topology_lock:
        with open(TOPOLOGY_FILENAME, 'w+b') as topology_file:
            if topology:
                pickle.dump(topology, topology_file)
            else:
                topology = pickle.load(topology_file)
    return dumps(topology.keys(), indent=2), 200, {'Content-Type': 'application/json'}



@app.route("/nsi/domains/<domain>")
@auto.doc()
def get_domain_ports(domain):
    """Get list of ports (Service Termination Points -STPs) in given NSI domain.
        
    Attributes:
        - domain: [string] URN identifier of of NSI domain 
                (eg.: 'urn:ogf:network:pionier.net.pl:2013:topology')
    
    Returns:
        1. HTTP code 200 and JSON list of URN identifiers of NSI ports in the domain
                (eg.: ["PORT_TO_PIONIER", "felix-ge-1-0-9'", "MDVPN__lab__port"])
    """
    ports = {}
    try:
        with topology_lock:
            topology = pickle.load(open(TOPOLOGY_FILENAME, 'rb'))
            
        if 'href' in topology[domain]:
            ports = get_domain_ports(topology[domain]['href'])
            topology[domain].update(ports)
            
            with topology_lock:
                pickle.dump(topology, open(TOPOLOGY_FILENAME, 'wb'))
        else:
            ports = topology[domain]
    except:
        import traceback
        app.logger.error(traceback.format_exc())
        
    return dumps(ports.keys(), indent=2), 200, {'Content-Type': 'application/json'}
        
        
    
@app.route("/nsi/domains/<domain>/port/<port>")
@auto.doc()
def get_domain_port_vlans(domain, port):
    """Get list of vlans in given port in the domain.
        
    Attributes:
        - domain: [string] URN identifier of of NSI domain 
                (eg.: 'urn:ogf:network:pionier.net.pl:2013:topology')
        - port: [string] port name 
                (eg.: 'elix-ge-1-0-9')
    
    Returns:
        1. HTTP code 200 and JSON object of VLAN properties of the port
                (eg.: {"vlans_in": "4-4096", "vlans_out": "4-4096")
    """
    try:
        with topology_lock:
            topology = pickle.load(open(TOPOLOGY_FILENAME, 'rb'))
        return jsonify(topology[domain][port])
    except:
        return jsonify([])
        
        
@app.route("/nsi/domains-full")
@auto.doc()
def get_domains_full():
    """Get list of NSI domains and its ports.
        
    Returns:
        1. HTTP code 200 and JSON object of URN identifiers of URN identifiers domains and ports
                (eg.: {"pionier.net.pl": ["PORT_TO_PIONIER", "felix-ge-1-0-9", "host2"],
                        "heanet.ie":["HEAnet-HRB-port", "HEANET-gsn-epa-port"]})
    """
    topology = get_nsi_topology(app.config["dds_service"])
    with topology_lock:
        with open(TOPOLOGY_FILENAME, 'w+b') as topology_file:
            if topology:
                pickle.dump(topology, topology_file)
            else:
                topology = pickle.load(topology_file)
    
    domain_url_list = []
    for domain, desc in topology.items():
        if 'href' in desc:
            domain_url_list.append((domain, topology[domain]['href']))
            del desc['href']
            
    def fetch(domain_url):
        try:
            domain, url = domain_url
            app.logger.info("Getting %s",url)
            data = urllib2.urlopen(url, timeout=1).read()
            app.logger.info("Data retrieved from %s", url)
            return domain, data
        except EnvironmentError as e:
            app.logger.info("Failing get %s", url)
            return domain, None
    
    pool = Pool(20)
    for domain, content in pool.imap_unordered(fetch, domain_url_list):
        if content:
            ports = parse_ports(content)
            topology[domain].update(ports)
            
    return jsonify(topology)
    
    
    
@app.route('/doc')
@auto.doc()
def documentation():
    """Generates HTML documentation of exposed REST API"""
    return auto.html(title='NSI ports REST API documentation')