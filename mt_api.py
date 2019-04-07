from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route('/list1')
def list1():
    d = [
            {
                "type": "MDList",
                "widgets": [
                            {
                                "type": "TwoLineListItem",
                                "text": "value1",
                                "secondary_text": "value1_small"
                            },
                            {
                                "type": "TwoLineListItem",
                                "text": "value2",
                                "secondary_text": "value2_small"
                            }
                        ]
            }
        ]
    return jsonify(d)

@app.route('/list2')
def list2():
    d = [{
        "type": "FloatLayout",
        "widgets": [{
            "type": "BoxLayout",
            "size": "root.size",
            "orientation": "vertical",
            "widgets": [{
                    "type": "AnchorLayout",
                    "anchor_x": 'center',
                    "anchor_y": 'top',
                    "widgets": [{
                            "type": "MDLabel",
                            "text": "[color=ff3333]Hello[/color][color=3333ff]World[/color]",
                            "id": "l1",
                            "size_hint_y": ".25",
                            "halign": "center",
                            "markup": True,
                            #"pos_hint": {'center_x': 0.5, 'center_y': 0.5}
                        }]
                        },
                {
                    "type": "AnchorLayout",
                    "anchor_x": 'center',
                    "anchor_y": 'top',
                    "widgets": [{
                            "type": "MDRaisedButton",
                            "text": "value2",
                            #"pos_hint": {'center_x': 0.5, 'center_y': 0.5},
                            "on_release": {
                                "api": "action1",
                            }
                        }]
                }]
                    }]
        }]
    return jsonify(d)

@app.route('/action1')
def action1():
    d = {
        "text": {
            "l1": "[color=ff3333][size=24]Button Clicked![/size][/color]"
        }
    }
    return jsonify(d)

@app.route('/getkvfile')
def getkvfile():
    with open("mt_layout.kv", 'r') as f:
        file_content = f.read()
    return file_content

@app.route('/getnav')
def getnav():
    d = {
        "the servers": "list1",
    }
    return jsonify(d)

@app.route('/getworknav')
def getworknav():
    d = {
        "the servers": "list1",
        "other stuff": "list2"
    }
    return jsonify(d)