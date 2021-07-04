import maya.cmds as cmds


def get_input(title, message):
    result = cmds.promptDialog(title=title,
                               message=message,
                               button=['Ok', 'Cancel'],
                               defaultButton='Ok',
                               cancelButton='Cancel',
                               dismissString='Cancel')

    if result == 'Ok':
        return cmds.promptDialog(query=True, text=True)

    return None
