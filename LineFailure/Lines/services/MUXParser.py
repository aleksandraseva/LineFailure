import os
import xml.etree.cElementTree as ET
from django.conf import settings
from django.db.models import Q

from Lines.models.Service import Service, Point, Route
from Lines.models.Connection import Connection


def find_all_service():
    for folder in os.listdir(settings.CONFIGURATIONS_PATH):
        path = os.path.join(settings.CONFIGURATIONS_PATH, folder)
        if os.path.isdir(path):
            for root, dirs, files in os.walk(path):
                for dir in dirs:
                    if dir in settings.ALLOWED_FOLDERS:
                        path = os.path.join(root, dir)
                        for root, dirs, files in os.walk(path):
                            for file in files:
                                if file == "common_config.xml":
                                    path_config_xml = os.path.join(root, file)
                                    try:
                                        tree = ET.parse(path_config_xml)
                                        root_xml = tree.getroot()
                                        element = None
                                        for element in root_xml.findall(
                                            "./MOB_CFG_AP/MOB_CFG_AP"
                                        ):
                                            if "port" in element.attrib.get("name", ""):
                                                name = element.attrib.get("name", "")
                                                main_tag = element.find(
                                                    "./MOB_CFG_MD[@name='main']"
                                                )
                                                if main_tag is not None:
                                                    labels_tag = main_tag.find(
                                                        "./MOB_CFG_DB[@name='labels']"
                                                    )
                                                    if labels_tag is not None:
                                                        uselLabel_tag = labels_tag.find(
                                                            ".//UserLabel"
                                                        )
                                                        if uselLabel_tag is not None:
                                                            if (
                                                                uselLabel_tag.text
                                                                is not None
                                                            ):
                                                                role = (
                                                                    uselLabel_tag.text
                                                                )
                                                                service = Service(
                                                                    name=role
                                                                )
                                                                service.save()
                                                                print(role)
                                                                find_next_point(
                                                                    element,
                                                                    folder,
                                                                    service,
                                                                )
                                    except Exception as e:
                                        print(e)


def find_next_point(element, location, service):
    ports_data = []
    isService = is_service(element)
    if isService:
        data = get_first_point(element, location, service)
        for unit, port, chan, route in data:
            get_seli_ports(location, unit, port, chan, route)


def get_seli_ports(location, unit, port, chan, route):
    try:
        next_location = None
        next_unit = None
        next_port = None
        next_connection = Connection.objects.filter(
            Q(first_location=location, first_unit=unit, first_port=port)
            | Q(second_location=location, second_unit=unit, second_port=port)
        )
        for connection in next_connection:
            if (
                connection.first_location == location
                and connection.first_unit == unit
                and connection.first_port == port
            ):
                next_location = connection.second_location
                next_unit = connection.second_unit
                next_port = connection.second_port
            else:
                next_location = connection.first_location
                next_unit = connection.first_unit
                next_port = connection.first_port
        if next_location and next_port and next_unit:
            xml_config = get_config(next_location, next_unit)
            if xml_config is not None:
                port_xml = get_port(xml_config, next_port)
                line_name = get_port_label(port_xml)
                point = Point(location=next_location, line_name=line_name)
                point.save()
                route.points.add(point)
                if not is_service(port_xml):
                    next_port_data = []
                    chan_xml = get_chan_port(port_xml, chan)
                    cfgm_tag = chan_xml.find("./MOB_CFG_MD[@name='cfgm']")
                    if cfgm_tag is not None:
                        for remote_tag in cfgm_tag.findall(
                            ".//remoteCtpDataList/remoteCtpData"
                        ):
                            ctp_ref = remote_tag.find("./ctpRef")
                            next_port_data.append(ctp_ref.text)
                    for data in next_port_data:
                        port_element = data.split("/")
                        next_config = find_config_unit_name(
                            next_location, port_element[1]
                        )
                        next_port = get_port(next_config, port_element[2])
                        line_name = get_port_label(next_port)
                        point = Point(location=next_location, line_name=line_name or "")
                        point.save()
                        route.points.add(point)
                        if not is_service(next_port):
                            get_seli_ports(
                                next_location,
                                port_element[1],
                                port_element[2],
                                port_element[3],
                                route,
                            )
                        else:
                            return
    except Exception as e:
        print(e)


def is_service(port_element):
    try:
        element = None
        for element in port_element.findall(f".//MOB_CFG_AP[@name]"):
            if element is not None:
                name = element.get("name")
                if name.startswith("chan-"):
                    return False
        return True
    except Exception as e:
        print(e)


def get_first_point(element, location, service):
    try:
        data = []
        return_data = []
        cfgm_tag = element.find("./MOB_CFG_MD[@name='cfgm']")
        if cfgm_tag is not None:
            for remote_tag in cfgm_tag.findall(".//remoteCtpDataList/remoteCtpData"):
                ctp_ref = remote_tag.find("./ctpRef")
                data.append(ctp_ref.text)
            for d in data:
                port_element = d.split("/")
                next_config = find_config_unit_name(location, port_element[1])
                port = get_port(next_config, port_element[2])
                line_name = get_port_label(port)
                route = Route(service=service)
                route.save()
                point = Point(location=location, line_name=line_name or "")
                point.save()
                route.points.add(point)
                return_data.append(
                    [port_element[1], port_element[2], port_element[3], route]
                )
        return return_data
    except Exception as e:
        print(e)


def find_config_unit_name(location, unit):
    path = os.path.join(settings.CONFIGURATIONS_PATH, location)
    if os.path.isdir(path):
        for root, dirs, files in os.walk(path):
            path_unit = os.path.join(path, "committed", unit)
            if not os.path.isdir(path):
                print(f"Folder ne postoji: {path}")
                break
            for root, dirs, files in os.walk(path_unit):
                for file in files:
                    if file == "common_config.xml":
                        return os.path.join(path_unit, file)


def get_port(config_xml, port):
    try:
        tree = ET.parse(config_xml)
        root = tree.getroot()
        element = None
        for element in root.findall(f".//MOB_CFG_AP[@name='{port}']"):
            if element is not None:
                return element
    except Exception as e:
        print(e)


def get_chan_port(port_element, chan):
    try:
        element = None
        for element in port_element.findall(f".//MOB_CFG_AP[@name='{chan}']"):
            if element is not None:
                return element
    except Exception as e:
        print(e)


def find_config_label(root_path, label):
    config_paths = []
    try:
        folders = os.listdir(root_path)
        for folder in folders:
            path = os.path.join(root_path, folder)
            for root, dirs, files in os.walk(path):
                if "common_config.xml" in files:
                    xml_path = os.path.join(root, "common_config.xml")
                    port = find_port_by_label(xml_path, label)
                    if port is not None:
                        config_paths.append(xml_path)
        return config_paths
    except Exception as e:
        print(e)


def find_port_by_label(config_xml, label):
    try:
        tree = ET.parse(config_xml)
        root = tree.getroot()
        element = None
        for element in root.findall("./MOB_CFG_AP/MOB_CFG_AP"):
            if "port" in element.attrib.get("name", ""):
                main_tag = element.find("./MOB_CFG_MD[@name='main']")
                if main_tag is not None:
                    labels_tag = main_tag.find("./MOB_CFG_DB[@name='labels']")
                    if labels_tag is not None:
                        uselLabel_tag = labels_tag.find(".//UserLabel")
                        if uselLabel_tag is not None:
                            if uselLabel_tag.text is not None:
                                if label in uselLabel_tag.text:
                                    return element
    except Exception as e:
        print(e)


def get_port_label(port_element):
    try:
        main_tag = port_element.find("./MOB_CFG_MD[@name='main']")
        if main_tag is not None:
            labels_tag = main_tag.find("./MOB_CFG_DB[@name='labels']")
            if labels_tag is not None:
                uselLabel_tag = labels_tag.find(".//UserLabel")
                if uselLabel_tag is not None:
                    return uselLabel_tag.text
    except Exception as e:
        print(e)


def get_config(location, unit):
    if not os.path.exists(settings.CONFIGURATIONS_PATH):
        print(f"Folder '{settings.CONFIGURATIONS_PATH}' ne postoji.")
        return None

    for folder in os.listdir(settings.CONFIGURATIONS_PATH):
        path = os.path.join(settings.CONFIGURATIONS_PATH, folder, "committed", unit)
        if os.path.isdir(path) and folder.lower().replace(" ", "").replace(
            "_", ""
        ) == location.lower().replace(" ", "").replace("_", ""):
            for root, dirs, files in os.walk(path):
                for file in files:
                    if file == "common_config.xml":
                        path_config_xml = os.path.join(root, file)

    return path_config_xml


def get_chan_port(port_element, chan):
    try:
        element = None
        for element in port_element.findall(f".//MOB_CFG_AP[@name='{chan}']"):
            if element is not None:
                return element
    except Exception as e:
        print(e)


if __name__ == "__main__":
    find_all_service()
