import sys
from flask import Flask
from raft import RaftBlueprint

app = Flask(__name__)
app.register_blueprint(RaftBlueprint.bp)
app.run(debug=True)
