import portal_client
import argparse

parser = argparse.ArgumentParser(
    description='Client to download data described by a manifest file ' + \
                'generated from a portal instance.'
)

parser.add_argument(
    '--version',
    action='version',
    version='%(prog)s ' + "noone cares"
)

parser.add_argument(
    '-m', '--manifest',
    type=str,
    help='Location of a locally stored manifest file.'
)

parser.add_argument(
    '-u', '--url',
    type=str,
    required=False,
    help='URL path to a manifest file stored at an HTTP endpoint.'
)

parser.add_argument(
    '--disable-validation',
    dest='disable_validation',
    action='store_true',
    help='Disable MD5 checksum validation.'
)

parser.add_argument(
    '-t', '--token',
    type=str,
    required=False,
    help='Token string generated for a cart from portal.ihmpdcc.org.'
)

parser.add_argument(
    '--google-client-secrets',
    type=str,
    required=False,
    dest='client_secrets',
    help='The path to a client secrets JSON file obtain from Google. ' + \
         'When using GCP (Google Cloud Platform) storage endpoints (' + \
         'urls that begin with "gs://"), this option is required.'
)

parser.add_argument(
    '--google-project-id',
    type=str,
    required=False,
    dest='project_id',
    help='The Google project ID to use. When using GCP (Google ' + \
          'Cloud Platform) storage endpoints, this option is required.'
)

parser.add_argument(
    '-d', '--destination',
    type=str,
    required=False,
    default=".",
    help='Optional location to place all the downloads. ' + \
         'Defaults to the current directory.'
)

parser.add_argument(
    '--endpoint-priority',
    type=str,
    required=False,
    default="",
    help='Optional comma-separated protocol priorities (descending). ' + \
         'The valid protocols are "HTTP", "FTP", "FASP", "S3" and "GS" ' + \
         '(and defaults to that order).'
)

parser.add_argument(
    '--user',
    type=str,
    required=False,
    help='The username to authenticate with when using Aspera ' + \
         'endpoints. All FASP (aspera) endpoints require ' + \
         'authentication. Note: Using --user will automatically ' + \
         'trigger an interactive request for a password.'
)

parser.add_argument(
    '-r', '--retries',
    type=int,
    required=False,
    default=0,
    help='Optional number of retries to perform in case of download ' + \
         'failures. Defaults to 0.'
)

parser.add_argument(
    '--debug',
    action='store_true',
    help='Display additional debugging information/logs at runtime.'
)

args = parser.parse_args(["--manifest", "aspera_manifest.tsv"])

# This is later populated if the user specifies the --user argument.
args.password = None

portal_client.parse_cli = lambda: args
portal_client.main()