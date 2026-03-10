import os
from .MUXParser import *


def get_folders(self, location):
    folders = []
    if not os.path.exists(self.root_folder):
        print(f"Folder '{self.root_folder}' ne postoji.")
        return folders

    for folder in os.listdir(self.root_folder):
        path = os.path.join(self.root_folder, folder)
        if os.path.isdir(path) and folder.lower().replace(" ", "").replace(
            "_", ""
        ) == location.lower().replace(" ", "").replace("_", ""):
            folders.append(folder)
    return folders


def find_config_freq():
    for folder in os.listdir("konfiguracije"):
        path = os.path.join("konfiguracije", folder)
        if os.path.isdir(path):
            for root, dirs, files in os.walk(path):
                for file in files:
                    if file == "common_config.xml":
                        path_config_xml = os.path.join(root, file)
                        elements = MUXParser.find_all_ports(path_config_xml)
                        for element in elements:
                            print(element)


if __name__ == "__main__":
    find_config_freq()


# folders = self.get_folders(location)
# for folder in folders:
#     path = os.path.join(self.root_folder, folder)
#     for root, dirs, files in os.walk(path):
#         for file in files:
#             if file == "common_config.xml":
#                 path_config_xml = os.path.join(root, file)
#                 element = XMLParser.find_port_by_label(
#                     path_config_xml, freq)
#                 if element is not None:
#                     root_element = element
#                     # location = config_dir.split()[0]
#                     unit = XMLParser.get_unit(path_config_xml)
#                     card = XMLParser.get_card_type(path_config_xml)
#                     port_name = XMLParser.get_port_name(root_element)
#                     freq = XMLParser.get_port_freq(root_element)
#                     loc_color=(location.replace(" ","").replace("(","_")).split(")")[0]
#                     try:
#                         color=self.colors[loc_color].value
#                     except KeyError:
#                         color="black"
#                     node = Node.Node(
#                         port_name, location, unit, freq, color)
#                     self.diagram.add_node(node)

#                     self.find_next_hop(root_element, location, node)

#                     break
