import sys
import os
import zlib
from hashlib import sha1


"""
form_path(sha1):
    Given sha1 hash of a git object, returns the file path to that object
"""
def form_path(sha_hash):
    return f".git/objects/{sha_hash[:2]}/{sha_hash[2:]}"


"""
compute_hash(filename): 
    Given filename, returns its hash and all its contents for processing
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
            obj = form_path(sys.argv[3])
            with open(obj, "rb") as f:
                rawdata = zlib.decompress(f.read())
                
                # removing header and leading and trailing whitespaces
                rawcontents = rawdata.split(b"\x00")[1].strip()
                
                orig = rawcontents.decode("utf-8")
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
            os.makedirs(f".git/objects/{obj_id[:2]}", exist_ok=True)
            path_to_file = form_path(obj_id)
            if not os.path.exists(path_to_file):
                with open(path_to_file, "wb") as f:
                    f.write(compressed_data)
        
        # object ID is printed either way
        print(obj_id)
        
    # git ls-tree
    elif git_command == "ls-tree":
        
        if len(sys.argv) == 3:
            # no flags provided
            is_name_only = False
            tree_hash = sys.argv[2]
        
        elif len(sys.argv) == 4 and sys.argv[2] == "--name-only":
            # git ls-tree --name-only
            is_name_only = True
            tree_hash = sys.argv[3]
        
        # reading and decompressing tree
        tree_path = form_path(tree_hash)
        with open(tree_path, "rb") as f:
            data = f.read()
        rawdata = zlib.decompress(data)
        
        # parsing tree
        tree_info = rawdata.split(b"\x00", maxsplit=1)[1]
        tree_contents = []
        while tree_info:
            
            # retrieving mode, filename, and SHA-1 hash
            modename, tree_info = tree_info.split(b"\x00", maxsplit=1)
            mode, name = modename.split()
            name = name.decode("utf-8")
            if is_name_only:
                # printing only the filename
                print(name)
            
            else: 
                mode = mode.decode("utf-8").zfill(6)
                sha_hash = tree_info[:20].hex()
                
                # preserving each record as a tuple
                tree_contents.append((mode, name, sha_hash))
            
            tree_info = tree_info[20:]
        
        if not is_name_only:
            for mode, name, sha_hash in tree_contents:
                if mode == "040000":
                    object_type = "tree"
                else:
                    object_type = "blob"
                tree_contains = f"{mode} {object_type} {sha_hash}\t{name}"
                print(tree_contains)    

            
    # unknown or unimplemented command
    else:
        raise RuntimeError(f"Unknown or unimplemented command #{git_command}")


if __name__ == "__main__":
    main()
