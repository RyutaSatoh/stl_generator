import subprocess
import os

def render_scad(scad_file_path, output_png_path, output_stl_path):
    # OpenSCAD を使用して PNG をレンダリング
    # --imgsize で解像度指定、--colorscheme で見た目を調整
    try:
        subprocess.run(
            [
                "openscad",
                "-o", output_png_path,
                "--imgsize=1024,768",
                "--colorscheme=DeepOcean",
                scad_file_path
            ],
            check=True,
            capture_output=True
        )
    except subprocess.CalledProcessError as e:
        return False, f"Error rendering PNG: {e.stderr.decode()}"

    # STL をエクスポート
    try:
        subprocess.run(
            [
                "openscad",
                "-o", output_stl_path,
                scad_file_path
            ],
            check=True,
            capture_output=True
        )
    except subprocess.CalledProcessError as e:
        return False, f"Error exporting STL: {e.stderr.decode()}"

    return True, None
