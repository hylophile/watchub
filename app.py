from flask import Flask, request, send_file, jsonify, render_template
import os
import pandas as pd
import subprocess

app = Flask(__name__)

@app.route('/<path:path>')
def index(path):
    # Get the path to the directory to be listed
    # dir_path = request.args.get('dir', '.')
    # dir_path = "/data/arr/media/tv"
    dir_path = os.path.abspath(f"/data/{path}")

    df = pd.read_csv("~/.config/mpv/hey.log", parse_dates=['datetime'])
    # Build a tree of files and directories
    tree = build_tree(df, dir_path)


    # Render the file tree using the template
    return render_template('index.html', tree=tree, render_node=render_node)

@app.route('/file-clicked', methods=['POST'])
def file_clicked():
    data = request.json
    file_path = data['filePath']
    
    try:
        subprocess.run(['mpv', file_path], check=True)
        return jsonify({'success': True})
    except subprocess.CalledProcessError as e:
        print('Error:', e)
        return jsonify({'success': False, 'error': str(e)})

def render_node(node):
    meter = f'''<meter min="0" max="100" low="0" high="50" optimum="90" value="{node["ratio"]}"></meter>'''
    if node['type'] == 'directory':
        child_nodes = ''.join([render_node(child) for child in node['children']])
        ratio = node['ratio']
        open = "open" if 0 < ratio < 90 else ""
        return f'<li class="directory {open}"><span>{meter} {node["name"]}</span><ul>{child_nodes}</ul></li>'
    else:
        return f'<li><span class="file" data-path="{node["path"]}">{meter} {node["name"]}</span></li>'

def build_tree(df, dir_path):
    # Initialize an empty tree
    tree = {'name': os.path.basename(dir_path), 'path': dir_path, 'type': 'directory', 'children': []}

    # Recursively add files and directories to the tree
    for filename in os.listdir(dir_path):
        file_path = os.path.join(dir_path, filename)
        if os.path.isdir(file_path):
            # Add a directory to the tree
            sub_tree = build_tree(df, file_path)
            tree['children'].append(sub_tree)
        else:
            # Add a file to the tree
            ratio = calculate_ratio_for_file(df, filename)
            file_node = {'name': filename, 'path': file_path, 'type': 'file', 'ratio':ratio}
            tree['children'].append(file_node)

    n_children = len(tree['children'])
    if n_children == 0:
        n_children = 1
    tree['ratio'] = sum([node['ratio'] for node in tree['children']]) / n_children

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

    file_df = df.loc[df['filename'] == filename]
    if file_df.empty:
        return 0

    last_row = file_df.iloc[-1]
    ratio = last_row['pos'] / last_row['duration']
    percent = int(round(ratio * 100))
    if percent > 90:
        percent = 100
    return percent


if __name__ == '__main__':
    app.run(debug=True)
