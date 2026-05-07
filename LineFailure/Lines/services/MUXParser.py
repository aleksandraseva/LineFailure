import hashlib
import os
import xml.etree.cElementTree as ET
from django.conf import settings
from django.db.models import Q
from django.db import transaction

from Lines.models.Service import Service, Point, Route, RoutePoint
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
                                                                    name=role,
                                                                    location=folder,
                                                                )
                                                                service.save()
                                                                print(role)
                                                                print(
                                                                    f"lokacija: {folder}"
                                                                )
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


def get_seli_ports(
    location,
    unit,
    port,
    chan,
    route,
    order=None,
    previous_unit=None,
    previous_ports=None,
    previous_location=None,
    previous_conf=False,
):
    try:
        if order is None:
            order = {"value": route.points.count() + 1}
        xml_config = get_config(location, unit)
        if xml_config is not None:
            port_xml = get_port(xml_config, port)
            chan_xml = get_chan_port(port_xml, chan)
            line_name = get_port_label(port_xml)
            point, created = Point.objects.get_or_create(
                location=location,
                line_name=line_name or "",
                port=port,
                unit=unit,
                chan=get_chan_name(chan_xml) if chan != "" else "",
            )
            RoutePoint.objects.create(
                route=route,
                point=point,
                order=order["value"],
            )
            order["value"] += 1
            if not is_service(port_xml):
                next_port_data = []
                cfgm_tag = chan_xml.find("./MOB_CFG_MD[@name='cfgm']")
                if cfgm_tag is not None:
                    for remote_tag in cfgm_tag.findall(
                        ".//remoteCtpDataList/remoteCtpData"
                    ):
                        ctp_ref = remote_tag.find("./ctpRef")
                        next_port_data.append(ctp_ref.text)
                for data in next_port_data:
                    port_element = data.split("/")
                    next_config = find_config_unit_name(location, port_element[1])
                    next_port = get_port(next_config, port_element[2])
                    if (
                        is_conf_port(next_port)
                        and port_element[1] != previous_unit
                        and port_element[2] != previous_ports
                    ):
                        get_seli_ports(
                            location=location,
                            unit=port_element[1],
                            port=port_element[2],
                            chan=port_element[3] if len(port_element) > 3 else "",
                            route=route,
                            order=order,
                            previous_unit=unit,
                            previous_ports=port,
                            previous_location=location,
                            previous_conf=previous_conf,
                        )
                    elif (
                        is_service(next_port)
                        and previous_unit is None
                        and previous_ports is None
                        and previous_location is None
                    ) or (
                        port_element[1] == previous_unit
                        and port_element[2] == previous_ports
                        and location == previous_location
                    ):
                        next_location = None
                        next_unit = None
                        next_port = None
                        next_connection = Connection.objects.filter(
                            Q(first_location=location, first_unit=unit, first_port=port)
                            | Q(
                                second_location=location,
                                second_unit=unit,
                                second_port=port,
                            )
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
                            get_seli_ports(
                                location=next_location,
                                unit=next_unit,
                                port=next_port,
                                chan=get_chan_name(chan_xml),
                                route=route,
                                order=order,
                                previous_unit=unit,
                                previous_ports=port,
                                previous_location=location,
                                previous_conf=previous_conf,
                            )
                    elif (
                        is_service(next_port)
                        and previous_unit is not None
                        and previous_ports is not None
                        and previous_location is not None
                    ):
                        line_name = get_port_label(next_port)
                        point, created = Point.objects.get_or_create(
                            location=location,
                            line_name=line_name or "",
                            port=port_element[2],
                            unit=port_element[1],
                            chan="",
                        )
                        RoutePoint.objects.create(
                            route=route,
                            point=point,
                            order=order["value"],
                        )
                        order["value"] += 1
                    else:
                        get_seli_ports(
                            location=location,
                            unit=port_element[1],
                            port=port_element[2],
                            chan=port_element[3] if len(port_element) > 3 else "",
                            route=route,
                            order=order,
                            previous_unit=unit,
                            previous_ports=port,
                            previous_location=location,
                            previous_conf=previous_conf,
                        )
            elif is_conf_port(port_xml) and not previous_conf:
                parts = get_parts_conf(port_xml)
                for part in parts:
                    role, data = get_role_part(part)
                    role = get_role(part)
                    role_route = Route(service=route.service, role=role)
                    role_route.save()
                    for port_data in data:
                        port_element = port_data.split("/")
                        get_seli_ports(
                            location=location,
                            unit=port_element[1],
                            port=port_element[2],
                            chan=(port_element[3] if len(port_element) > 3 else ""),
                            route=role_route,
                            order=None,
                            previous_unit=unit,
                            previous_ports=port,
                            previous_location=location,
                            previous_conf=True,
                        )
            elif is_conf_port(port_xml) and previous_conf:
                print("AAAA")
            else:
                return
        else:
            return
    except Exception as e:
        print(e)


def remove_duplicate_routes():
    unique = {}
    for route in Route.objects.all():
        key = tuple(sorted(route.points.values_list("id", flat=True)))
        if key in unique:
            route.delete()
        else:
            unique[key] = route.id


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


def is_conf_port(element):
    try:
        element_name = element.attrib.get("name", "")
        if element_name.startswith("conf-"):
            return True
        return False
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
            for i, d in enumerate(data):
                port_element = d.split("/")
                next_config = find_config_unit_name(location, port_element[1])
                port = get_port(next_config, port_element[2])
                line_name = get_port_label(port)
                route = Route(service=service, role="")
                route.save()
                point, created = Point.objects.get_or_create(
                    location=location,
                    line_name=line_name or "",
                    port=port_element[2],
                    unit=port_element[1],
                    chan=port_element[3],
                )
                print("service ID:", service.id)
                print("ROUTE ID:", route.id)
                RoutePoint.objects.create(
                    route=route,
                    point=point,
                    order=1,
                )
                print("ROUTE ID: poslije", route.id)
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


def get_port_name(element):
    try:
        port_name = element.attrib.get("name", "")
        return port_name
    except Exception as e:
        print(e)


def get_chan_name(chan):
    try:
        chan_name = chan.attrib.get("name", "")
        return chan_name
    except Exception as e:
        print(e)


def get_parts_conf(conf_element):
    parts = []
    try:
        element = None
        for element in conf_element.findall(".//MOB_CFG_AP"):
            if element is not None:
                name = element.get("name")
                if name.startswith("part-"):
                    parts.append(element)
        return parts
    except Exception as e:
        print(e)


def get_role(part):
    try:
        element = None
        for element in part.findall(".//MOB_CFG_DB[@name='general']"):
            if element is not None:
                role_tag = element.find(".//role")
                if role_tag is not None:
                    return role_tag.text
    except Exception as e:
        print(e)


def get_role_part(conf_element):
    parts = []
    try:
        role = None
        for role in conf_element.findall(".//MOB_CFG_DB[@name='general']"):
            if role is not None:
                role_tag = conf_element.find(".//role")
                ports = []
                cfgm_tag = conf_element.find("./MOB_CFG_MD[@name='cfgm']")
                if cfgm_tag is not None:
                    for remote_tag in cfgm_tag.findall(
                        ".//remoteCtpDataList/remoteCtpData"
                    ):
                        ctpRef = remote_tag.find("./ctpRef")
                        ports.append(ctpRef.text)
                return (role_tag.text, ports)
    except Exception as e:
        print(e)


if __name__ == "__main__":
    find_all_service()
