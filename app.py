from flask import Flask, render_template, jsonify
import subprocess
import os

app = Flask(__name__)

# Ensure the template folder is correctly set
template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'templates'))
app.template_folder = template_dir

def get_git_info():
    try:
        branch = subprocess.check_output(['git', 'branch', '--show-current']).decode().strip()
        last_commit = subprocess.check_output(['git', 'log', '-1', '--pretty=format:%h - %s']).decode()
        return {'branch': branch, 'last_commit': last_commit}
    except:
        return {'branch': 'unknown', 'last_commit': 'none'}

@app.route('/')
def dashboard():
    try:
        return render_template('index.html', git_info=get_git_info())  # Changed from dashboard.html to index.html
    except Exception as e:
        return f"""
        <h1>Setup Guide</h1>
        <p>Error: {str(e)}</p>
        <p>Template Directory: {app.template_folder}</p>
        <p>Files in Template Dir: {os.listdir(app.template_folder) if os.path.exists(app.template_folder) else 'Directory not found'}</p>
        """

@app.route('/api/status')
def status():
    git_info = get_git_info()
    return jsonify({
        'status': 'active',
        'git': git_info,
        'project_name': 'Prometheus Bot'
    })

if __name__ == '__main__':
    print(f"Template directory: {app.template_folder}")
    print(f"Current directory: {os.getcwd()}")
    app.run(debug=True, port=3000)