import os
import runpy
import sys


def main() -> None:
    root_dir = os.path.dirname(os.path.abspath(__file__))
    backend_dir = os.path.join(root_dir, "backend")
    server_path = os.path.join(backend_dir, "server.py")

    os.chdir(root_dir)
    if backend_dir not in sys.path:
        sys.path.insert(0, backend_dir)

    runpy.run_path(server_path, run_name="__main__")


if __name__ == "__main__":
    main()
