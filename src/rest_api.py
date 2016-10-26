import logging, pickle, threading, urllib2
from multiprocessing.dummy import Pool
from flask import Flask, jsonify
from json import dumps
from flasgger import Swagger
from port_retrieval import get_nsi_topology, parse_ports


app = Flask(__name__)
Swagger(app)

topology_lock = threading.Lock()

#~ import logging_tree
#~ logging_tree.printout()

TOPOLOGY_FILENAME = 'topology.pkl'


@app.route("/nsi/domains")
def get_domains():
    """
    Get list of NSI domains registered in NSI AG
    --- 
    tags:
        - NSI domains
    responses:
        200:
            description: Returns list of URN identifiers of NSI domains registered in NSI AG
            schema: 
                type: array
                items:
                    description: URI identifier of NSI domain, example urn:ogf:network:pionier.net.pl:2013:topology
                    type: string
    """  
    topology = get_nsi_topology(app.config["dds_service"])
    with topology_lock:
        with open(TOPOLOGY_FILENAME, 'w+b') as topology_file:
            if topology:
                pickle.dump(topology, topology_file)
            else:
                topology = pickle.load(topology_file)
    return dumps(topology.keys(), indent=2), 200, {'Content-Type': 'application/json'}



@app.route("/nsi/domains/<string:domain>/ports")
def get_domain_ports(domain):
    """
    Get list of ports in given NSI domain
    ---
    tags:
        - NSI domains
    parameters:
        -   name: domain
            in: path
            description: URN identifier of NSI domain, example urn:ogf:network:pionier.net.pl:2013:topology
            type: string
    responses:
        200: 
            description: list of URN identifiers of ports in the NSI domain
            schema:
                type: array
                items:
                    description: port name
                    type: string
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
        
        
    
@app.route("/nsi/domains/<string:domain>/ports/<string:port>")
def get_domain_port_vlans(domain, port):
    """
    Get vlans for given port in the NSI domain
    ---   
    tags:
        - NSI domains    
    parameters:
        -   name: domain
            description: URN identifier of NSI domain, example urn:ogf:network:pionier.net.pl:2013:topology
            in: path
            type: string
            required: true
        -   name: port
            in: path
            description: port name
            type: string
            required: true            
    responses:
        200: 
            description: VLAN properties of the port
            schema:
                properties:
                    vlans_in:
                        type: string
                        description: list of incoming VLANs acceptable for NSI domain, example 4-2000,3000-4096
                        required: true
                    vlans_out:
                        type: string
                        description: list of outgoing VLANs acceptable for NSI domain, example 4-2000,3000-4096
                        required: true
    """
    try:
        with topology_lock:
            topology = pickle.load(open(TOPOLOGY_FILENAME, 'rb'))
        return jsonify(topology[domain][port])
    except:
        return jsonify([])
        
        
@app.route("/nsi/domains-full")
def get_domains_full():
    """
    Get list of NSI domains and its ports
    ---
    tags:
        - NSI domains
    responses:
        200:
            description: Returns list of NSI domains, its ports and vlan attributes
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
    