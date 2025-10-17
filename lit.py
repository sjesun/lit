import sys
import os
import zlib


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
        
        # git cat-file -p: pretty-print
        if sys.argv[2] == "-p":
            sha_hash = sys.argv[3]
            obj = f".git/objects/{sha_hash[0:2]}/{sha_hash[2:]}"
            with open(obj, "rb") as f:
                rawdata = zlib.decompress(f.read())
                
                # removing header and leading and trailing whitespaces
                rawcontents = rawdata.split(b"\x00")[1].strip()
                
                orig = rawcontents.decode()
                print(orig, end="")
        
        # other valid flags (-e, -t, -s, etc.) or invalid flags
        else:
            raise RuntimeError(f"Unknown or unimplemented flag #{sys.argv[2]}")
    
    # unknown or unimplemented command
    else:
        raise RuntimeError(f"Unknown or unimplemented command #{git_command}")


if __name__ == "__main__":
    main()
