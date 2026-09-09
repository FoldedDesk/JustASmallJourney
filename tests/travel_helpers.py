"""Force server routing only when testing rewards for a particular location."""
from unittest.mock import patch


def travel(client, body, **kwargs):
    body = dict(body)
    destination = body.pop('place', 'forest')
    # Concurrent legacy tests use the fixture's fixed forest route, without
    # swapping a global mock around concurrent requests.
    if destination == 'forest':
        return client.post('/api/travel', json=body, **kwargs)
    with patch('app.choose_destination', return_value=destination):
        return client.post('/api/travel', json=body, **kwargs)
