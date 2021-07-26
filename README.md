# Microservice Repository Template

This repo is a template for creating a new microservice.

The directories, files, and their structure herein are recommendations
from the GHGA Dev Team.

## Naming Conventions
The github repository contains only lowercase letters, numbers, and hyphens "-",
e.g.: `my-microservice`

The python package (and thus the source repository) contains underscores "_"
instead of hyphens, e.g.: `my_microservice`

The command-line script that is used to run the service, the docker repository
(published to docker hub), and the helm chart (not part of this repository) use the
same pattern as the repository name, e.g.: `my-microservice`
## Adapt to your service
This is just a template and needs some adaption to your specific use case.

Please search for "Please adapt to package" comments to find all locations
that need modification and then remove them after your modifications.
