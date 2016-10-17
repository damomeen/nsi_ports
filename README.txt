# Copyright 2016 Poznan Supercomputing and Networking Center
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

nsi_ports
----------------

1. Overview

'nsi_ports' exposes HTTP/REST JSON API for quering information about GEANT BoD and GLIF AutoGOLE domains and clients ports. 
The information are gathered using HTTP DDS service from NSI Aggregator (AG) specified in the configuration.

Documents presenting OGF NSI Topology Service:
    - https://redmine.ogf.org/projects/nsi-wg-topology/repository/revisions/master/changes/draft-gwdi-nsi-topology-service.pdf
    - https://redmine.ogf.org/projects/nsi-wg-topology/repository/revisions/master/changes/draft-gwdrp-nsi-topology-representation.pdf
    
    
1.1 REST API specification

    1. GET /nsi/domains
    
        Get list of NSI domains registeres in NSI AG
        
        Returns:
            1. HTTP code 200 and JSON list of URN identifiers of NSI domains registered in NSI AG
                    (eg.: ["urn:ogf:network:geant.net:2013:topology", "urn:ogf:network:heanet.ie:2013:topology"])
            
    2. GET /nsi/domains/<domain_name>
    
        Get list of ports (Service Termination Points -STPs) in given NSI domain.
        
        Attributes:
            - domain_name: [string] URN identifier of of NSI domain 
                    (eg.: 'urn:ogf:network:pionier.net.pl:2013:topology')
        
        Returns:
            1. HTTP code 200 and JSON list of URN identifiers of NSI ports in the domain
                    (eg.: ["PORT_TO_PIONIER", "felix-ge-1-0-9'", "MDVPN__lab__port"])
                    
    3. GET /nsi/domains-full
    
        Get list of NSI domains and its ports.
        
        Returns:
            1. HTTP code 200 and JSON object of URN identifiers of URN identifiers domains and ports
                    (eg.: {"pionier.net.pl": ["PORT_TO_PIONIER", "felix-ge-1-0-9", "host2"],
                            "heanet.ie":["HEAnet-HRB-port", "HEANET-gsn-epa-port"]})
                            
    4. GET /nsi/domains/doc 
    
        Generates HTML documentation of exposed REST API
        
        
        
2. Installation

2.1 Requirements

Needs Python and Flask installed:
    - Python 2.7 (https://www.python.org/)
    - Flask 0.11.1 (http://flask.pocoo.org)
    - Flask-Autodoc 0.1.2 (https://github.com/acoomans/flask-autodoc)
    
    1. Install python libraries by pip:
        pip install Flask Flask-Autodoc
        
2.2 Download 'nsi_ports' from github
    
    git clone https://github.com/damomeen/nsi_ports.git


3. Setup

    1. create configuration file from an example
        From root of the project do
        cd ./nsi_ports/etc
        cp nsi_ports.conf.example nsi_ports.conf
        
    2. edit nsi_ports.conf
    
        {
            "port":9001,
            "dds_service": "https://agg.netherlight.net2/dds"
        }
    
    3. add right to execute ./nsi_ports/src/nsi_ports
        chmod +x ./nsi_ports/src/nsi_ports
        
    4. add ./nsi_ports/src to PATH environment variable in order to allow run 'nsi_ports' anywhere.
        Make this permament in '.bashrc', '.bash_profile', etc.
        cd ./nsi_ports/src
        export PATH=$PATH:`pwd`
        
        
        
        
4. Start up

    1. run 'nsi_ports' service from any location:
        nsi_ports start
        
    2. stop 'nsi_ports' service from any location:
        nsi_ports stop
        
    3. check REST API documentation in web browser:
        http://localhost:9000/nsi/domains/doc
        
    4. make testing usage of REST API:
        curl http://localhost:9001/nsi/domains
        curl http://localhost:9001/nsi/domains-full
        
    5. Enable default TCP ports in the firewall:
        - 9001: HTTP REST/API service
        
