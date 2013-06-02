Fusion-Tables-CMD
=================
When accessing Google Fusion Tables with a [Service Account](https://developers.google.com/accounts/docs/OAuth2ServiceAccount) (for server to server communication), you don't have access to the Web API.

This is a simple command line tool for listing, creating, and deleting tables.

## Usage

```
python main.py -k key.p12 -i google_service_id@developer.gserviceaccount.com
```

```
Usage: main.py [options]
-k and -i are required.

Options:
  -h, --help         show this help message and exit
  -k KEY, --key=KEY  p12 key
  -i GID, --id=GID   service account id
```

## Opinions
This app is currently opinionated: created tables default to public and have yellow location markers.

## Dependencies

* google-api-python-client
* httplib2
* readline (for autocompletion)

## License
Released under the Simplified BSD License.
