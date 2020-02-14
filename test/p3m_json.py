import os
import struct
import json


def import_p3m(filepath, hide_unused_bones):
    model_name = os.path.basename(filepath)

    print("[Importing %s]" % model_name)

    model_name = os.path.splitext(model_name)[0]

    file_object = open(filepath, 'rb')

    file_object.read(27)  # skips the version

    # if data_chunk != 'Perfact 3D Model (Ver 0.5)\0':
    #    return

    print("Reading bones...")

    data = file_object.read(2)
    bone_position_count, bone_angle_count = struct.unpack('<2B', data)

    print("Bone position count: " + str(bone_position_count))
    print("Bone angle count: " + str(bone_angle_count))

    bone_positions = [None] * bone_position_count
    for x in range(bone_position_count):
        data = file_object.read(3 * 4)
        px, py, pz = struct.unpack('<3f', data)
        children_angles = []

        for _ in range(10):
            data = file_object.read(1)
            angle_index, = struct.unpack('<1B', data)

            if angle_index != 255:
                children_angles.append(angle_index)

        bone_positions[x] = [{"x": px, "y": py, "z": pz}, {"children_angles": children_angles}]

        file_object.read(2)  # ignores the padding

    bone_angles = [None] * bone_angle_count
    for x in range(bone_angle_count):
        file_object.read(4 * 4)

        children_positions = []

        for _ in range(10):
            data = file_object.read(1)
            position_index, = struct.unpack('<1B', data)

            if position_index != 255:
                children_positions.append(position_index)

        bone_angles[x] = children_positions

        file_object.read(2)  # ignores the padding

    """
    bone_angles_children = []
    for x in range(bone_angle_count):
        children_indexes = []

        for pos in bone_angles[x]:
            for ang in bone_positions[pos][1]:
                children_indexes.append(ang)

        bone_angles_children.append(children_indexes)
    """

    print("Reading mesh...")

    data = file_object.read(4)
    vertex_count, face_count = struct.unpack('<2H', data)

    file_object.read(260)  # ignores the texture_filename

    print("Reading faces...")

    faces = []

    for x in range(face_count):
        data = file_object.read(3 * 2)
        a, b, c = struct.unpack('<3H', data)

        faces.append({"a": a, "b": b, "c": c})

    print("Reading vertices...")

    vertices = []
    for x in range(vertex_count):
        data = file_object.read(40)
        px, py, pz, weight, index, nx, ny, nz, tu, tv = struct.unpack('<3f1f1B3x3f2f', data)

        if index != 255:
            index = index - bone_position_count

        tv = 1 - tv

        vertices.append({"index": index, "weight": weight, "position": {"x": px, "y": py, "z": pz}, "normal": {"x": nx, "y": ny, "z": nz}, "texture": {"u": tu, "v": tv}})

    print("Bulding JSON...")

    final_json = {
        "bone_position_count": bone_position_count,
        "bone_angle_count": bone_angle_count,
        "bone_positions": bone_positions,
        "bone_angles": bone_angles,
        "vertex_count": vertex_count,
        "vertices": vertices,
        "face_count": face_count,
        "faces": faces,
    }

    file = open("p3m_decompressed.json", "w")
    file.write(json.dumps(final_json))
    file.close()


if __name__ == "__main__":
    import_p3m(r"E:\PycharmProjects\P3M_Import_Export\test\untitled.p3m", "")
