import urllib2
import xml.etree.ElementTree as ElementTree
import base64
import pprint
from cStringIO import StringIO
from gzip import GzipFile
import xmltodict

import logging
logger = logging.getLogger(__name__)

# Remove namespaces during xml parsing
namespaces = {
    "http://schemas.ogf.org/nml/2013/05/base#" : None,
    "http://schemas.ogf.org/nsi/2013/09/topology#"  : None,
    "http://schemas.ogf.org/nsi/2013/12/services/definition"  : None,
    "http://schemas.ogf.org/nml/2014/01/ethernet" : None,
    "http://schemas.ogf.org/nsi/2014/02/discovery/nsa" : None,
    "urn:ietf:params:xml:ns:vcard-4.0" : None,
    "http://nordu.net/namespaces/2013/12/gnsbod" : None,
}


def simpler_domain_name(full_name):
    return full_name.split(':')[3]
    
    
def get_port_name(urn_name):
    return ':'.join(urn_name.split(':')[6:])
    
    
def iter_seq_or_one(sequance_or_one):
    'interface can be list dict if many interfaces or just dict if only one interface'
    if type(sequance_or_one) is list:
            for interface in sequance_or_one:
                yield interface
    else:
        yield sequance_or_one
        
    
    
def parse_domain_description(data):
    data = base64.b64decode(data)
    data = GzipFile('', 'r', 0, StringIO(data)).read()  # ungziping data
    try:
        d = xmltodict.parse(data, process_namespaces=True, namespaces=namespaces)
        if 'Topology' in d:
            return parse_domain_ports(d)
        
        for interface in iter_seq_or_one(d['nsa']['interface']):
            if 'vnd.ogf.nsi.topology' in interface['type']:
                dds_domain_link =  interface['href']
                return {'href':dds_domain_link}
    except:
        logger.error(data)
        import traceback
        logger.error(traceback.format_exc())
        return {}
        
        
        
def parse_ports(data):
    try:
        data = xmltodict.parse(data, process_namespaces=True, namespaces=namespaces)
        return parse_domain_ports(data)
    except:
        import traceback
        logger.error(traceback.format_exc())
        return {}



def parse_domain_ports(data):
    ports = data['Topology']['BidirectionalPort']
    relations = data['Topology']['Relation']
    
    _ports = {}
    for port in ports:
        name = get_port_name(port['@id'])
        _ports[name] = {'vlans_in':'', 'vlans_out':'', 'portgroups':[]}
        for portgroup in port['PortGroup']:
            _ports[name]['portgroups'].append(portgroup['@id'])
                
    def search_port(portgroup):
        for portname in _ports:
            portgroups = _ports[portname]['portgroups']
            if portgroup in portgroups:
                return portname
        return None
        
    def clean_portgroups():
        for portname in _ports:
            del _ports[portname]['portgroups']

    for relation in relations:
        if 'hasInboundPort' in relation['@type']:
            direction = 'vlans_in'
        elif 'hasOutboundPort' in relation['@type']:
            direction = 'vlans_out'
        else: 
            continue
        for pg in iter_seq_or_one(relation['PortGroup']):
            portgroup = pg['@id']
            vlans = pg['LabelGroup']['#text']
            port = search_port(portgroup)
            if port in _ports:
                _ports[port][direction] = vlans
            else:
                logger.warning('Port not found %s for portgroup %s', port, portgroup)

    clean_portgroups()
    return _ports



def get_nsi_topology(dds_service_url):
    topology = {}
    try:
        data = urllib2.urlopen(dds_service_url).read()
        root = ElementTree.fromstring(data)
        for child in root:
            if child.tag != "{http://schemas.ogf.org/nsi/2014/02/discovery/types}documents":
                continue
            for child2 in child:
                domain_name = child2.attrib['id']
                domain_data = child2.find('content').text
                ports = parse_domain_description(domain_data)
                if ports != None:
                    topology[domain_name] = ports
    except:
        import traceback
        logger.error(traceback.format_exc())
    return topology
    


