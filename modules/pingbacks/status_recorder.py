import os
import json
import datetime


class StatusRecorder:
    def __init__(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        self.status_recorder = json.load(open(os.path.join(dir_path, 'status-recorder-config.json')))

    def clear(self):
        with open(self.status_recorder.get('status_store'), 'w') as f:
            f.write(json.dumps([], indent=4, sort_keys=True))

    def add(self, entity_uri):
        new_entity_status = {
            'uri': entity_uri,
            'strategies': [0],
            'first_attempt': datetime.datetime.now().isoformat(),
            'last_attempt': None,
            'dereferencable': False,
            'rdf_metadata': False,
            'pingback_endpoints': None,
            'provenance_endpoints': None,
            'pingback_received': False,
            'provenance_bundle_received': False
        }
        with open(self.status_recorder.get('status_store'), 'r') as f:
            entities = json.load(f)
        entities.append(new_entity_status)
        with open(self.status_recorder.get('status_store'), 'w') as f:
            f.write(json.dumps(entities, indent=4, sort_keys=True))

        return new_entity_status

    def load(self, entity_uri):
        # check for existing entities with this URI
        with open(self.status_recorder.get('status_store'), 'r') as f:
            entities = json.load(f)

        for entity in entities:
            if entity['uri'] == entity_uri:
                return entity

        # entity not in store so create a new one, write to store and return
        return self.add(entity_uri)

    def update(self, entity_uri, updated_fields):
        with open(self.status_recorder.get('status_store'), 'r') as f:
            entities = json.load(f)

        for entity in entities:
            if entity['uri'] == entity_uri:
                for field in updated_fields.items():
                    entity[field[0]] = field[1]

        with open(self.status_recorder.get('status_store'), 'w') as f:
            f.write(json.dumps(entities, indent=4, sort_keys=True))

        return True
