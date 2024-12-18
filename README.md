# pi-client

A client for the Pi project.

# Install

```bash
pip install git+https://github.com/crunchdao/pi-client.git#egg_name=pi
```

# Usage

```python
import pi

# will read api key from CRUNCHDAO_PI_API_KEY
client = pi.api.Client()

# test if it is working
print(client.get_current_user())
```
