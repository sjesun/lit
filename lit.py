import sys
import os
import zlib
from hashlib import sha1


"""
compute_hash(filename): 
    Given filename, returns its hash and all its contents for processing by 
    'git hash-object'
"""
def compute_hash(filename):
    with open(filename, "rb") as f:
        contents = f.read()
    whole = f"blob {len(contents)}\x00".encode("utf-8") + contents
    object_id = sha1(whole).hexdigest()
    return object_id, whole


def main():
    git_command = sys.argv[1]
    
    # git init
    if git_command == "init":
        os.mkdir(".git")
        os.mkdir(".git/objects")
        os.mkdir(".git/refs")
        with open(".git/HEAD", "w") as f:
            f.write("ref: refs/heads/main\n")
        print("Git directory initialized.")
    
    # git cat-file
    elif git_command == "cat-file":
    
        if sys.argv[2] == "-p":
            # git cat-file -p: pretty-print
            sha_hash = sys.argv[3]
            subdirectory, filename = sha_hash[:2], sha_hash[2:]
            obj = f".git/objects/{subdirectory}/{filename}"
            with open(obj, "rb") as f:
                rawdata = zlib.decompress(f.read())
                
                # removing header and leading and trailing whitespaces
                rawcontents = rawdata.split(b"\x00")[1].strip()
                
                orig = rawcontents.decode()
                print(orig, end="")
        
        else:
            # other valid flags (-e, -t, -s, etc.) or invalid flags
            raise RuntimeError(f"Unknown or unimplemented flag #{sys.argv[2]}")
    
    # git hash-object
    elif git_command == "hash-object":
        
        if len(sys.argv) == 3:
            # no flags provided
            obj_id, data = compute_hash(sys.argv[2])
        
        elif len(sys.argv) == 4 and sys.argv[2] == "-w":
            # git hash-object -w
            obj_id, data = compute_hash(sys.argv[3])
            
            # preparing data for writing
            compressed_data = zlib.compress(data)
            subdirectory, file = obj_id[:2], obj_id[2:]
            os.makedirs(f".git/objects/{subdirectory}", exist_ok=True)
            path = f".git/objects/{subdirectory}/{file}"
            with open(path, "wb") as f:
                f.write(compressed_data)
        
        # object ID is printed either way
        print(obj_id)
    
    # unknown or unimplemented command
    else:
        raise RuntimeError(f"Unknown or unimplemented command #{git_command}")


if __name__ == "__main__":
    main()
