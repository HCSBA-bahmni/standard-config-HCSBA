## Default Bahmni configuration and data for Bahmni Standard
======================================================================

This repository holds the Bahmni Configurations for Bahmni Standard with CIEL dictionary for metadata.

This repo has been forked from Bahmni/default-config and CIEL metadata is added on top of it.

Refer Bahmni Wiki for detailed explanation of each configuration: https://bahmni.atlassian.net/wiki/spaces/BAH/pages/2392073/Implementer+s+Guide

## Docker Image Build
The docker image bahmni/standard-config is generated using Github Actions. 

In order to build the image in local you can run the following command
```shell
docker build -t bahmni/standard-config -f package/docker/Dockerfile .
```

To dockerise your implementation specific config repository, follow the steps below:
1. Copy the package/docker directory to your repository
2. Add/ remove COPY statements in Dockerfile based on the needs.
3. Run the following command after updating image repository and image name.
    > docker build -t {repository}/{image-name} -f package/docker/Dockerfile .
4. Also you can add Github Actions from `.github/workflows` directory.



Se cambia 
Drug Dosing Units Concept Uuid
d45d6060-5e07-11ef-8f7c-0242ac120002
Por 
162384AAAAAAAAAAAAAAAAAAAAAAAAAAAAAA


Dosing Instructions Concept Uuid ( se agregaron los conceptos en español con csv)
d46ee786-5e07-11ef-8f7c-0242ac120002

Drug Dispensing Units Concept Uuid no tiene

Drug Routes Concept Uuid
d462489d-5e07-11ef-8f7c-0242ac120002

Duration Units Concept Uuid
1732AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA


order frequency se cambia en la base de datos, pero hace referencia a conceptos.
id conceptiod frequency per day
1	81	1.0
2	82	2.0
3	83	3.0
4	84	4.0
5	100	24.0
6	101	12.0
7	102	8.0
8	103	6.0
9	104	4.0
10	105	3.0
11	106	2.0
12	107	0.5
13	108	0.142857142
14	109	0.285714285
15	110	0.428571428
16	111	0.071428571
17	112	0.047619047
18	113	0.033333333
19	121	5.0
20	122	0.571428571
21	123	0.714285714
22	124	0.857142857
23	92	1.0

se agregan estos concoptos tambien respetando los uuid