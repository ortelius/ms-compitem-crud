# ortelius-ms-compitem-crud

![Release](https://img.shields.io/github/v/release/ortelius/ms-compitem-crud?sort=semver)
![license](https://img.shields.io/github/license/ortelius/ms-compitem-crud)

![Build](https://img.shields.io/github/actions/workflow/status/ortelius/ms-compitem-crud/build-push-chart.yml)
[![MegaLinter](https://github.com/ortelius/ms-compitem-crud/workflows/MegaLinter/badge.svg?branch=main)](https://github.com/ortelius/ms-compitem-crud/actions?query=workflow%3AMegaLinter+branch%3Amain)
![CodeQL](https://github.com/ortelius/ms-compitem-crud/workflows/CodeQL/badge.svg)
[![OpenSSF
-Scorecard](https://api.securityscorecards.dev/projects/github.com/ortelius/ms-compitem-crud/badge)](https://api.securityscorecards.dev/projects/github.com/ortelius/ms-compitem-crud)

![Discord](https://img.shields.io/discord/722468819091849316)


Component Details Microservice - CRUD

## API LIST

Three types of APIs are supported at the moment.

### Add list of component item

```bash
curl localhost:5000/msapi/compitem?comp_id=255
```

Returns:

```json
[{"id": 361, "compid": 255, "buildid": "", "buildurl": "", "dockersha": "", "dockertag": "", "gitcommit": "", "gitrepo": "", "giturl": ""},
{"id": 8000, "compid": 255, "buildid": "test", "buildurl": "test", "dockersha": "test", "dockertag": "test", "gitcommit": "test", "gitrepo": "test", "giturl": "test"},
{"id": 8001, "compid": 255, "buildid": "test", "buildurl": "test", "dockersha": "test", "dockertag": "test", "gitcommit": "test", "gitrepo": "test", "giturl": "test"}]
```

### Delete list of component item

```bash
curl -X DELETE localhost:5000/msapi/compitem?comp_id=339
```

### Get list of component item

```bash
curl localhost:5000/msapi/compitem?comp_id=106
```

## Run the app

`$ python main.py`

## Fixed CVEs

- 2/27/23 - [CVE-2023-25139](https://www.openwall.com/lists/oss-security/2023/02/10/1)
