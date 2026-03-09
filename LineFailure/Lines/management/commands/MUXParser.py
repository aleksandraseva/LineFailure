import os
import xml.etree.cElementTree as ET
from django.conf import settings


def find_all_service():
    for folder in os.listdir(settings.CONFIGURATIONS_PATH):
        path = os.path.join(settings.CONFIGURATIONS_PATH, folder)
        if os.path.isdir(path):
            for root, dirs, files in os.walk(path):
                for dir in dirs:
                    if dir in settings.ALLOWED_FOLDERS:
                        for folder in files:
                            if file == "common_config.xml":
                                path_config_xml = os.path.join(root, file)
                                elements = MUXParser.find_all_ports(path_config_xml)
                                for element in elements:
                                    print(element)


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


if __name__ == "__main__":
    find_all_service()
