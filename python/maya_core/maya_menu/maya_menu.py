import json

import pymel.core as pm


def create_menus(d, parent=None):
    if "submenus" in d.keys():
        if d['lbl'] == "top_level":
            _ = [create_menus(a, parent) for a in d['submenus']]
        else:
            menu_parent = pm.menuItem(label=d['lbl'], subMenu=True, parent=parent, tearOff=True)
            _ = [create_menus(a, menu_parent) for a in d['submenus']]
    elif "cmd" in d.keys():
        pm.menuItem(label=d['lbl'], subMenu=False, parent=parent, tearOff=False, command=d["cmd"])
    elif "divider" in d.keys():
        pm.menuItem(divider=True, parent=parent)


def create_studio_menu():
    MAYA_MAIN_WINDOW = pm.language.melGlobals['gMainWindow']
    menu_json_path = r"F:\share\tools\tools_core\python\maya_core\maya_menu\menus.json"

    json_file = open(menu_json_path, "r")
    menu_json_data = json.load(json_file)
    json_file.close()

    menu_name, menu_label = 'StudioMenu', 'Studio'

    if pm.menu(menu_name, label=menu_label, exists=True):
        pm.deleteUI(pm.menu(menu_name, e=1, deleteAllItems=1))

    studio_menu = pm.menu(menu_name, label=menu_label, parent=MAYA_MAIN_WINDOW, tearOff=1)

    menu_data = menu_json_data

    create_menus(menu_data, parent=studio_menu)


if __name__ == '__main__':
    create_studio_menu()
