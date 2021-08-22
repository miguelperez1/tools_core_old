import maya.cmds as cmds
import pymel.core as pm
import mash_repro_utils as repro


def create_mash_network(mash_data):
    network_name = mash_data['name']
    geo_type = mash_data['geo_type']
    distribute_type = mash_data['distribute_type']
    scatter_amount = mash_data['scatter_amount']
    mesh = mash_data['mesh']
    objects = mash_data['objects']
    random = mash_data['random']
    mash_random = None

    mash_waiter = pm.createNode("MASH_Waiter", n=network_name)
    mash_distribute = pm.createNode("MASH_Distribute", n="{}_Distribute".format(network_name))

    if mesh:
        try:
            m = pm.PyNode(mesh)
            pm.connectAttr(m.worldMesh, mash_distribute.inputMesh)
        except Exception:
            print("Could not connect mesh: {} to distribute".format(mesh))

    if random:
        mash_random = pm.createNode("MASH_Random", n="{}_Random".format(network_name))

    mash_id = pm.createNode("MASH_Id", n="{}_Id".format(network_name))

    if geo_type == "Instancer":
        mash_instancer = pm.createNode("instancer", n="{}_Instancer".format(network_name))

        # add instancer message attribute
        pm.addAttr(mash_waiter, ln="instancerMessage", at="message")
        pm.addAttr(mash_instancer, ln="instancerMessage", at="message")

        pm.connectAttr(mash_waiter.outputPoints, mash_instancer.inputPoints)
        pm.connectAttr(mash_waiter.instancerMessage, mash_instancer.instancerMessage)

        for i, obj in enumerate(objects):
            try:
                cmds.connectAttr("{}.matrix".format(str(obj)), "{0}.inputHierarchy[{1}]".format(str(mash_instancer), i))
                obj.visibility.set(0)
            except Exception:
                print("Could not add {} to mash instancer".format(str(obj)))

    elif geo_type == "Mesh":
        mesh = pm.createNode("mesh", n="{}_ReproMesh".format(network_name))

        try:
            pm.delete(mesh.getShape())
        except Exception:
            pass

        mash_repro = pm.createNode("MASH_Repro", n="{}_Repro".format(network_name))

        pm.addAttr(mash_waiter, ln="instancerMessage", at="message")
        pm.addAttr(mash_repro, ln="instancerMessage", at="message")

        pm.connectAttr(mash_waiter.outputPoints, mash_repro.inputPoints)
        pm.connectAttr(mash_waiter.instancerMessage, mash_repro.instancerMessage)

        pm.connectAttr(mash_repro.outMesh, mesh.inMesh)
        pm.connectAttr(mesh.message, mash_repro.meshMessage)
        pm.connectAttr(mesh.worldInverseMatrix, mash_repro.meshMatrix)

        for i, obj in enumerate(objects):
            try:
                repro.connect_mesh_group(str(mash_repro), str(obj))
                obj.visibility.set(0)
            except Exception:
                print("Could not add {} to mash instancer".format(str(obj)))

    # Connect everything else

    #   Connect distribute to waiter
    pm.connectAttr(mash_distribute.waiterMessage, mash_waiter.waiterMessage)

    #   Connect ID/Random chain
    pm.connectAttr(mash_distribute.outputPoints, mash_id.inputPoints)

    if mash_random is not None:
        pm.connectAttr(mash_id.outputPoints, mash_random.inputPoints)
        pm.connectAttr(mash_random.outputPoints, mash_waiter.inputPoints)
    else:
        pm.connectAttr(mash_id.outputPoints, mash_waiter.inputPoints)

    # Set Attrs
    mash_distribute.pointCount.set(scatter_amount)
    mash_distribute.arrangement.set(distribute_type)



    mash_id.numObjects.set(len(objects))

    mash_random.positionX.set(0)
    mash_random.positionY.set(0)
    mash_random.positionZ.set(0)

    mash_random.rotationX.set(5)
    mash_random.rotationY.set(180)
    mash_random.rotationZ.set(5)

    mash_random.scaleX.set(0.5)
    mash_random.uniformRandom.set(1)
    mash_random.transformationSpace.set(2)
