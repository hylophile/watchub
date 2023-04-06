from flask import Flask, request, send_file, jsonify, render_template
import os
import pandas as pd
import subprocess
import re

app = Flask(__name__)

wh_pipe_path = os.environ.get("WH_PIPE_PATH")
wh_root_path = os.environ.get("WH_ROOT_PATH") or "/data/"
wh_mpv_log = os.environ.get("WH_MPV_LOG") or "~/.config/mpv/hey.log"
wh_port = os.environ.get("WH_PORT") or "5959"
wh_debug = True if os.environ.get("WH_DEBUG") == "1" else False


@app.route("/<path:path>")
def index(path):
    # Get the path to the directory to be listed
    # dir_path = request.args.get('dir', '.')
    # dir_path = "/data/arr/media/tv"
    dir_path = os.path.abspath(f"{wh_root_path}/{path}")

    df = pd.read_csv(f"{wh_mpv_log}", parse_dates=["datetime"])
    # Build a tree of files and directories
    tree = build_tree(df, dir_path)

    # Render the file tree using the template
    return render_template("index.html", tree=tree, render_node=render_node)


@app.route("/file-clicked", methods=["POST"])
def file_clicked():
    data = request.json
    file_path = data["filePath"]

    try:
        if wh_pipe_path is not None:
            with open(wh_pipe_path, "w") as pipe:
                pipe.write(file_path)
        else:
            subprocess.run(["mpv", file_path], check=True)
        return jsonify({"success": True})
    except subprocess.CalledProcessError as e:
        print("Error:", e)
        return jsonify({"success": False, "error": str(e)})


def render_node(node):
    meter = f"""<meter min="0" max="100" low="0" high="50" optimum="90" value="{node["ratio"]}"></meter>"""
    if node["type"] == "directory":
        child_nodes = "".join(
            [
                render_node(child)
                for child in sorted(node["children"], key=lambda d: d["name"])
            ]
        )
        ratio = node["ratio"]
        # open = "open" if 0 < ratio < 90 else ""
        return f'<li class="directory" data-path="{node["path"]}"><div>{meter}<span class="dirname"> {node["name"]}</span></div><ul>{child_nodes}</ul></li>'
    else:
        short_name, is_episode = extract_episode(node["name"])
        episode_attr = "data-is-episode" if is_episode else ""

        return f'<li class="file" title="{node["name"]}" data-full-name="{node["name"]}" {episode_attr}  data-short-name="{short_name}" data-path="{node["path"]}"><div class="cont">{meter}<span class="filename" >{node["name"]}</span></div></li>'


def build_tree(df, dir_path):
    # Initialize an empty tree
    tree = {
        "name": os.path.basename(dir_path),
        "path": dir_path,
        "type": "directory",
        "children": [],
    }

    # Recursively add files and directories to the tree
    for filename in os.listdir(dir_path):
        file_path = os.path.join(dir_path, filename)
        if os.path.isdir(file_path):
            # Add a directory to the tree
            sub_tree = build_tree(df, file_path)
            tree["children"].append(sub_tree)
        else:
            # Add a file to the tree
            if filename.endswith((".mkv", ".mp4", ".avi")):
                ratio = calculate_ratio_for_file(df, filename)
                file_node = {
                    "name": filename,
                    "path": file_path,
                    "type": "file",
                    "ratio": ratio,
                }
                tree["children"].append(file_node)

    n_children = len(tree["children"])
    if n_children == 0:
        n_children = 1
    tree["ratio"] = sum([node["ratio"] for node in tree["children"]]) / n_children

    return tree


def calculate_ratio_for_file(df, filename):
    """
    Reads a CSV file with columns 'datetime', 'filename', 'pos', and 'duration',
    finds the last row in the DataFrame with the given filename, and calculates
    the ratio of pos to duration rounded to an integer.

    Parameters:
        filename (str): The name of the file to calculate the ratio for.
        filepath (str): The path to the CSV file.

    Returns:
        int: The ratio of pos to duration rounded to an integer.
    """

    file_df = df.loc[df["filename"] == filename]
    if file_df.empty:
        return 0

    last_row = file_df.iloc[-1]
    try:
        ratio = float(last_row["pos"]) / float(last_row["duration"])
    except:
        ratio = 0

    percent = int(round(ratio * 100))

    if percent > 90:
        percent = 100
    return percent


def extract_episode(string):
    pattern = r"[sS]\d\d[eE]\d\d"
    matches = re.findall(pattern, string)
    if matches:
        first_match = matches[0]
        return re.findall(r"[eE]\d\d", first_match)[0].upper(), True
    else:
        return (
            string,
            False,
        )


if __name__ == "__main__":
    app.run(debug=wh_debug, port=wh_port, host="0.0.0.0")
