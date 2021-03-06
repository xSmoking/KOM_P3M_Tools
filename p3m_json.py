import os
import getopt
import struct
import json
import sys


def import_p3m(argv):
    if len(argv) < 2:
        sys.exit(2)

    try:
        options, arguments = getopt.getopt(argv, 'i:o:', ['in=', 'out='])
    except getopt.GetoptError:
        sys.exit(2)

    in_path = None
    out_path = None

    for option, argument in options:
        if option in ('i', '--in'):
            in_path = argument
        elif option in ('o', '--out'):
            out_path = argument

    if in_path is None or out_path is None:
        sys.exit(2)

    file_name = os.path.basename(in_path)

    print("[Importing %s]" % file_name)

    model_name = os.path.splitext(file_name)[0]

    file_object = open(in_path, 'rb')

    file_object.read(27)  # skips the version

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
            px += bone_positions[index][0]['x']
            py += bone_positions[index][0]['y']
            pz += bone_positions[index][0]['z']

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

    file = open(out_path, "w")
    file.write(json.dumps(final_json))
    file.close()


if __name__ == "__main__":
    import_p3m(sys.argv[1:])

