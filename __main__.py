import os
import os.path as path
import glob
import io
import struct

def derle(input: io.BytesIO, output: io.BytesIO):
    if input.read(1) != b'\x30':
        raise Exception("Unknown compression method")

    decompressed_size = struct.unpack("<I", input.read(3) + b'\x00')[0]

    out_size = 0
    while out_size < decompressed_size:
        flag = input.read(1)[0]
        compressed = (flag & 0x80) > 0
        length = flag & 0x7F
        if compressed:
            length += 3
        else:
            length += 1

        if out_size + length > decompressed_size:
            raise Exception("Invalid compressed data")

        if compressed:
            seq = input.read(1) * length
            if len(seq) < length:
                raise Exception("Stream exhausted")
            out_size += output.write(seq)
        else:
            seq = input.read(length)
            if len(seq) < length:
                raise Exception("Stream exhausted")
            out_size += output.write(seq)

def unpack(f: io.BytesIO, base_dir: str, archive_name: str):
    version_maybe = f.read(2)
    if version_maybe != b'\x03\x00':
        raise Exception("Unknown version")

    file_count = struct.unpack("<h", f.read(2))[0]
    data_start = struct.unpack("<I", f.read(4))[0]

    files = []
    for _ in range(file_count):
        file = {}
        files.append(file)
        file["name"] = f.read(64).decode("utf-8").rstrip("\x00")
        file["size_uncompressed"] = struct.unpack("<I", f.read(4))[0]
        file["size_compressed"] = struct.unpack("<I", f.read(4))[0]
        file["data_offset"] = data_start + struct.unpack("<I", f.read(4))[0]

    for file in files:
        print(f"  {file["name"]}")
        out_path = path.join(base_dir, f"[{archive_name}]" + file["name"])
        #out_path_compressed = path.join(base_dir, f"[{archive_name}]" + file["name"][:-1] + "_")
        with open(out_path, "wb") as out:
            f.seek(file["data_offset"])
            derle(io.BytesIO(f.read(file["size_compressed"])), out)
        #with open(out_path_compressed, "wb") as out:
        #    f.seek(file["data_offset"])
        #    out.write(f.read(file["size_compressed"]))

root = "C:\\Users\\Dobby\\Downloads\\deltawarriors_lightnerinicepalace\\jp_data"
for archive_path in glob.iglob("**/*.bin", root_dir=root, recursive=True):
    print(archive_path)

    if "story" in archive_path and archive_path.endswith(".lst.bin"):
        print("    compiled script file?")
        continue

    archive_path = path.join(root, archive_path)
    with open(archive_path, "rb") as f:
        unpack(f, path.dirname(archive_path), path.splitext(path.basename(archive_path))[0])
    os.remove(archive_path)