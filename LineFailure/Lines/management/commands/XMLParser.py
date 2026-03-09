import os
import xml.etree.cElementTree as ET

from Lines.models.Port import Port


def find_all_ports(config_xml, location):
    try:
        ports = []
        tree = ET.parse(config_xml)
        root = tree.getroot()
        element = None
        for element in root.findall("./MOB_CFG_AP/MOB_CFG_AP"):
            if "port" in element.attrib.get("name", ""):
                name = element.attrib.get("name", "")
                main_tag = element.find("./MOB_CFG_MD[@name='main']")
                if main_tag is not None:
                    labels_tag = main_tag.find("./MOB_CFG_DB[@name='labels']")
                    if labels_tag is not None:
                        uselLabel_tag = labels_tag.find(".//UserLabel")
                        if uselLabel_tag is not None:
                            if uselLabel_tag.text is not None:
                                role = uselLabel_tag.text

        return ports
    except Exception as e:
        print(e)
