import urllib2
import xml.etree.ElementTree as ElementTree
import base64
import pprint
from cStringIO import StringIO
from gzip import GzipFile

import logging
logger = logging.getLogger(__name__)

# Object not used because I experianced problems in using NameSpaces in ElementTree library
#ns = {'ns2': 'http://schemas.ogf.org/nsi/2014/02/discovery/types'}

def simpler_domain_name(full_name):
    return full_name.split(':')[3]
    
    
def get_domain_ports(data):
    data = base64.b64decode(data)
    data = GzipFile('', 'r', 0, StringIO(data)).read()  # ungziping data
    root = ElementTree.fromstring(data)
    for child in root:
        if child.tag != "{http://schemas.ogf.org/nml/2013/05/base#}BidirectionalPort":
            continue
        for child2 in child:
            if child2.tag == "{http://schemas.ogf.org/nml/2013/05/base#}name":
                yield child2.text
                

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
                ports = list(get_domain_ports(domain_data))
                if len(ports) == 0:
                    continue
                #TODO: analyse NSA string: child2.find('nsa').text if required
                topology[domain_name] = ports
    except:
        import traceback
        logger.debug(traceback.format_exc())
    return topology
    


