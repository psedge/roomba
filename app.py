import redis
import hashlib
import json
from flask import Flask, request, jsonify

app = Flask(__name__)
r = redis.Redis(host='redis', port=6379, db=0)

@app.route("/", methods=['POST'])
def run():
    '''
    Default route, takes JSON body and runs algorithm to calculate how many
    patches of dirt are swept up by a Roomba following directions.
    '''

    body = request.get_json()
    try:
        room_size = body['roomSize']
        position = body['coords']
        patches = body['patches'].copy()
        instructions = body['instructions']
    except KeyError as e:
        app.logger.error('Incorrect JSON structure POSTed.')
        return jsonify(success=False), 400

    key = hashlib.sha256()
    key.update((str(room_size) + str(position) + str(patches) + instructions).encode("UTF-8"))
    cached = r.get(key.digest().hex())
    if cached is not None:
        app.logger.info("Fetched: " + key.digest().hex())
        return jsonify(json.loads(cached))

    # Detect if we cleaned a patch of dirt
    def clean(position, patches):
        if position in patches:
            return patches.remove(position)
    
    # Clean our starting patch
    clean(position, patches)

    for direction in instructions:
        # Shift positions
        position[0] += 1 if direction is 'E' else -1 if direction is 'W' else 0
        position[1] += 1 if direction is 'N' else -1 if direction is 'S' else 0
        
        # Undo if we've breached the wall
        position[0] += 1 if position[0] < 0 else -1 if position[0] > room_size[0] else 0
        position[1] += 1 if position[1] < 0 else -1 if position[1] > room_size[1] else 0
        
        # Clean current position
        clean(position, patches)
        
        app.logger.info('cPos: ' + str(position) + ' | dir: ' + direction + ' | patches: ' + str(patches))
    
    # Store to DB, return
    res = {'coords': position, 'patches': len(body['patches']) - len(patches)}
    r.set(key.digest().hex(), json.dumps(res))
    return jsonify(res)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
