# ortelius-ms-compitem-crud

![Release](https://img.shields.io/github/v/release/ortelius/ms-compitem-crud?sort=semver)
![license](https://img.shields.io/github/license/ortelius/.github)

![Build](https://img.shields.io/github/actions/workflow/status/ortelius/ms-compitem-crud/build-push-chart.yml)
[![MegaLinter](https://github.com/ortelius/ms-compitem-crud/workflows/MegaLinter/badge.svg?branch=main)](https://github.com/ortelius/ms-compitem-crud/actions?query=workflow%3AMegaLinter+branch%3Amain)
![CodeQL](https://github.com/ortelius/ms-compitem-crud/workflows/CodeQL/badge.svg)
[![OpenSSF
-Scorecard](https://api.securityscorecards.dev/projects/github.com/ortelius/ms-compitem-crud/badge)](https://api.securityscorecards.dev/projects/github.com/ortelius/ms-compitem-crud)

![Discord](https://img.shields.io/discord/722468819091849316)

> Version 0.1.0

ortelius-ms-compitem-crud

## Path Table

| Method | Path                                    | Description     |
|--------|-----------------------------------------|-----------------|
| GET    | [/health](#gethealth)                   | Health          |
| GET    | [/msapi/compitem](#getmsapicompitem)    | Get Compitem    |
| POST   | [/msapi/compitem](#postmsapicompitem)   | Create Compitem |
| DELETE | [/msapi/compitem](#deletemsapicompitem) | Delete Compitem |
| PUT    | [/msapi/compitem](#putmsapicompitem)    | Update Compitem |

## Reference Table

| Name                | Path                                                                              | Description |
|---------------------|-----------------------------------------------------------------------------------|-------------|
| CompItemModel       | [#/components/schemas/CompItemModel](#componentsschemascompitemmodel)             |             |
| HTTPValidationError | [#/components/schemas/HTTPValidationError](#componentsschemashttpvalidationerror) |             |
| StatusMsg           | [#/components/schemas/StatusMsg](#componentsschemasstatusmsg)                     |             |
| ValidationError     | [#/components/schemas/ValidationError](#componentsschemasvalidationerror)         |             |

## Path Details

***

### [GET]/health

- Summary  
Health

- Operation id  
health_health_get

- Description  
This health check end point used by Kubernetes

#### Responses

- 200 Successful Response

`application/json`

```typescript
{
  status?: string
  service_name?: string
}
```

***

### [GET]/msapi/compitem

- Summary  
Get Compitem

- Operation id  
get_compitem_msapi_compitem_get

#### Parameters(Query)

```typescript
compitemid: integer
```

```typescript
comptype?: Partial(string) & Partial(null)
```

#### Responses

- 200 Successful Response

`application/json`

```typescript
{
  compid?: integer
  id?: integer
  builddate?: Partial(string) & Partial(null)
  buildid?: Partial(string) & Partial(null)
  buildurl?: Partial(string) & Partial(null)
  chart?: Partial(string) & Partial(null)
  chartnamespace?: Partial(string) & Partial(null)
  chartrepo?: Partial(string) & Partial(null)
  chartrepourl?: Partial(string) & Partial(null)
  chartversion?: Partial(string) & Partial(null)
  created?: Partial(integer) & Partial(null)
  creatorid?: Partial(integer) & Partial(null)
  discordchannel?: Partial(string) & Partial(null)
  dockerrepo?: Partial(string) & Partial(null)
  dockersha?: Partial(string) & Partial(null)
  dockertag?: Partial(string) & Partial(null)
  gitcommit?: Partial(string) & Partial(null)
  gitrepo?: Partial(string) & Partial(null)
  gittag?: Partial(string) & Partial(null)
  giturl?: Partial(string) & Partial(null)
  hipchatchannel?: Partial(string) & Partial(null)
  kind?: Partial(string) & Partial(null)
  modified?: Partial(integer) & Partial(null)
  modifierid?: Partial(integer) & Partial(null)
  name?: Partial(string) & Partial(null)
  pagerdutybusinessurl?: Partial(string) & Partial(null)
  pagerdutyurl?: Partial(string) & Partial(null)
  predecessorid?: Partial(integer) & Partial(null)
  purl?: Partial(string) & Partial(null)
  repository?: Partial(string) & Partial(null)
  rollback?: Partial(integer) & Partial(null)
  rollup?: Partial(integer) & Partial(null)
  serviceowner?: Partial(string) & Partial(null)
  serviceowneremail?: Partial(string) & Partial(null)
  serviceownerid?: Partial(string) & Partial(null)
  serviceownerphone?: Partial(string) & Partial(null)
  slackchannel?: Partial(string) & Partial(null)
  status?: Partial(string) & Partial(null)
  summary?: Partial(string) & Partial(null)
  targetdirectory?: Partial(string) & Partial(null)
  xpos?: Partial(integer) & Partial(null)
  ypos?: Partial(integer) & Partial(null)
  scorecardpinned?: Partial(string) & Partial(null)
  scorecardscore?: Partial(string) & Partial(null)
  binaryartifacts?: Partial(string) & Partial(null)
  branchprotection?: Partial(string) & Partial(null)
  ciibestpractices?: Partial(string) & Partial(null)
  codereview?: Partial(string) & Partial(null)
  dangerousworkflow?: Partial(string) & Partial(null)
  fuzzing?: Partial(string) & Partial(null)
  license?: Partial(string) & Partial(null)
  maintained?: Partial(string) & Partial(null)
  packaging?: Partial(string) & Partial(null)
  pinneddependencies?: Partial(string) & Partial(null)
  sast?: Partial(string) & Partial(null)
  securitypolicy?: Partial(string) & Partial(null)
  signedreleases?: Partial(string) & Partial(null)
  tokenpermissions?: Partial(string) & Partial(null)
  vulnerabilities?: Partial(string) & Partial(null)
}[]
```

- 422 Validation Error

`application/json`

```typescript
{
  detail: {
    loc?: Partial(string) & Partial(integer)[]
    msg: string
    type: string
  }[]
}
```

***

### [POST]/msapi/compitem

- Summary  
Create Compitem

- Operation id  
create_compitem_msapi_compitem_post

#### RequestBody

- application/json

```typescript
{
  compid?: integer
  id?: integer
  builddate?: Partial(string) & Partial(null)
  buildid?: Partial(string) & Partial(null)
  buildurl?: Partial(string) & Partial(null)
  chart?: Partial(string) & Partial(null)
  chartnamespace?: Partial(string) & Partial(null)
  chartrepo?: Partial(string) & Partial(null)
  chartrepourl?: Partial(string) & Partial(null)
  chartversion?: Partial(string) & Partial(null)
  created?: Partial(integer) & Partial(null)
  creatorid?: Partial(integer) & Partial(null)
  discordchannel?: Partial(string) & Partial(null)
  dockerrepo?: Partial(string) & Partial(null)
  dockersha?: Partial(string) & Partial(null)
  dockertag?: Partial(string) & Partial(null)
  gitcommit?: Partial(string) & Partial(null)
  gitrepo?: Partial(string) & Partial(null)
  gittag?: Partial(string) & Partial(null)
  giturl?: Partial(string) & Partial(null)
  hipchatchannel?: Partial(string) & Partial(null)
  kind?: Partial(string) & Partial(null)
  modified?: Partial(integer) & Partial(null)
  modifierid?: Partial(integer) & Partial(null)
  name?: Partial(string) & Partial(null)
  pagerdutybusinessurl?: Partial(string) & Partial(null)
  pagerdutyurl?: Partial(string) & Partial(null)
  predecessorid?: Partial(integer) & Partial(null)
  purl?: Partial(string) & Partial(null)
  repository?: Partial(string) & Partial(null)
  rollback?: Partial(integer) & Partial(null)
  rollup?: Partial(integer) & Partial(null)
  serviceowner?: Partial(string) & Partial(null)
  serviceowneremail?: Partial(string) & Partial(null)
  serviceownerid?: Partial(string) & Partial(null)
  serviceownerphone?: Partial(string) & Partial(null)
  slackchannel?: Partial(string) & Partial(null)
  status?: Partial(string) & Partial(null)
  summary?: Partial(string) & Partial(null)
  targetdirectory?: Partial(string) & Partial(null)
  xpos?: Partial(integer) & Partial(null)
  ypos?: Partial(integer) & Partial(null)
  scorecardpinned?: Partial(string) & Partial(null)
  scorecardscore?: Partial(string) & Partial(null)
  binaryartifacts?: Partial(string) & Partial(null)
  branchprotection?: Partial(string) & Partial(null)
  ciibestpractices?: Partial(string) & Partial(null)
  codereview?: Partial(string) & Partial(null)
  dangerousworkflow?: Partial(string) & Partial(null)
  fuzzing?: Partial(string) & Partial(null)
  license?: Partial(string) & Partial(null)
  maintained?: Partial(string) & Partial(null)
  packaging?: Partial(string) & Partial(null)
  pinneddependencies?: Partial(string) & Partial(null)
  sast?: Partial(string) & Partial(null)
  securitypolicy?: Partial(string) & Partial(null)
  signedreleases?: Partial(string) & Partial(null)
  tokenpermissions?: Partial(string) & Partial(null)
  vulnerabilities?: Partial(string) & Partial(null)
}[]
```

#### Responses

- 200 Successful Response

`application/json`

```typescript
{}
```

- 422 Validation Error

`application/json`

```typescript
{
  detail: {
    loc?: Partial(string) & Partial(integer)[]
    msg: string
    type: string
  }[]
}
```

***

### [DELETE]/msapi/compitem

- Summary  
Delete Compitem

- Operation id  
delete_compitem_msapi_compitem_delete

#### Parameters(Query)

```typescript
compid: integer
```

#### Responses

- 200 Successful Response

`application/json`

```typescript
{}
```

- 422 Validation Error

`application/json`

```typescript
{
  detail: {
    loc?: Partial(string) & Partial(integer)[]
    msg: string
    type: string
  }[]
}
```

***

### [PUT]/msapi/compitem

- Summary  
Update Compitem

- Operation id  
update_compitem_msapi_compitem_put

#### RequestBody

- application/json

```typescript
{
  compid?: integer
  id?: integer
  builddate?: Partial(string) & Partial(null)
  buildid?: Partial(string) & Partial(null)
  buildurl?: Partial(string) & Partial(null)
  chart?: Partial(string) & Partial(null)
  chartnamespace?: Partial(string) & Partial(null)
  chartrepo?: Partial(string) & Partial(null)
  chartrepourl?: Partial(string) & Partial(null)
  chartversion?: Partial(string) & Partial(null)
  created?: Partial(integer) & Partial(null)
  creatorid?: Partial(integer) & Partial(null)
  discordchannel?: Partial(string) & Partial(null)
  dockerrepo?: Partial(string) & Partial(null)
  dockersha?: Partial(string) & Partial(null)
  dockertag?: Partial(string) & Partial(null)
  gitcommit?: Partial(string) & Partial(null)
  gitrepo?: Partial(string) & Partial(null)
  gittag?: Partial(string) & Partial(null)
  giturl?: Partial(string) & Partial(null)
  hipchatchannel?: Partial(string) & Partial(null)
  kind?: Partial(string) & Partial(null)
  modified?: Partial(integer) & Partial(null)
  modifierid?: Partial(integer) & Partial(null)
  name?: Partial(string) & Partial(null)
  pagerdutybusinessurl?: Partial(string) & Partial(null)
  pagerdutyurl?: Partial(string) & Partial(null)
  predecessorid?: Partial(integer) & Partial(null)
  purl?: Partial(string) & Partial(null)
  repository?: Partial(string) & Partial(null)
  rollback?: Partial(integer) & Partial(null)
  rollup?: Partial(integer) & Partial(null)
  serviceowner?: Partial(string) & Partial(null)
  serviceowneremail?: Partial(string) & Partial(null)
  serviceownerid?: Partial(string) & Partial(null)
  serviceownerphone?: Partial(string) & Partial(null)
  slackchannel?: Partial(string) & Partial(null)
  status?: Partial(string) & Partial(null)
  summary?: Partial(string) & Partial(null)
  targetdirectory?: Partial(string) & Partial(null)
  xpos?: Partial(integer) & Partial(null)
  ypos?: Partial(integer) & Partial(null)
  scorecardpinned?: Partial(string) & Partial(null)
  scorecardscore?: Partial(string) & Partial(null)
  binaryartifacts?: Partial(string) & Partial(null)
  branchprotection?: Partial(string) & Partial(null)
  ciibestpractices?: Partial(string) & Partial(null)
  codereview?: Partial(string) & Partial(null)
  dangerousworkflow?: Partial(string) & Partial(null)
  fuzzing?: Partial(string) & Partial(null)
  license?: Partial(string) & Partial(null)
  maintained?: Partial(string) & Partial(null)
  packaging?: Partial(string) & Partial(null)
  pinneddependencies?: Partial(string) & Partial(null)
  sast?: Partial(string) & Partial(null)
  securitypolicy?: Partial(string) & Partial(null)
  signedreleases?: Partial(string) & Partial(null)
  tokenpermissions?: Partial(string) & Partial(null)
  vulnerabilities?: Partial(string) & Partial(null)
}[]
```

#### Responses

- 200 Successful Response

`application/json`

```typescript
{}
```

- 422 Validation Error

`application/json`

```typescript
{
  detail: {
    loc?: Partial(string) & Partial(integer)[]
    msg: string
    type: string
  }[]
}
```

## References

### #/components/schemas/CompItemModel

```typescript
{
  compid?: integer
  id?: integer
  builddate?: Partial(string) & Partial(null)
  buildid?: Partial(string) & Partial(null)
  buildurl?: Partial(string) & Partial(null)
  chart?: Partial(string) & Partial(null)
  chartnamespace?: Partial(string) & Partial(null)
  chartrepo?: Partial(string) & Partial(null)
  chartrepourl?: Partial(string) & Partial(null)
  chartversion?: Partial(string) & Partial(null)
  created?: Partial(integer) & Partial(null)
  creatorid?: Partial(integer) & Partial(null)
  discordchannel?: Partial(string) & Partial(null)
  dockerrepo?: Partial(string) & Partial(null)
  dockersha?: Partial(string) & Partial(null)
  dockertag?: Partial(string) & Partial(null)
  gitcommit?: Partial(string) & Partial(null)
  gitrepo?: Partial(string) & Partial(null)
  gittag?: Partial(string) & Partial(null)
  giturl?: Partial(string) & Partial(null)
  hipchatchannel?: Partial(string) & Partial(null)
  kind?: Partial(string) & Partial(null)
  modified?: Partial(integer) & Partial(null)
  modifierid?: Partial(integer) & Partial(null)
  name?: Partial(string) & Partial(null)
  pagerdutybusinessurl?: Partial(string) & Partial(null)
  pagerdutyurl?: Partial(string) & Partial(null)
  predecessorid?: Partial(integer) & Partial(null)
  purl?: Partial(string) & Partial(null)
  repository?: Partial(string) & Partial(null)
  rollback?: Partial(integer) & Partial(null)
  rollup?: Partial(integer) & Partial(null)
  serviceowner?: Partial(string) & Partial(null)
  serviceowneremail?: Partial(string) & Partial(null)
  serviceownerid?: Partial(string) & Partial(null)
  serviceownerphone?: Partial(string) & Partial(null)
  slackchannel?: Partial(string) & Partial(null)
  status?: Partial(string) & Partial(null)
  summary?: Partial(string) & Partial(null)
  targetdirectory?: Partial(string) & Partial(null)
  xpos?: Partial(integer) & Partial(null)
  ypos?: Partial(integer) & Partial(null)
  scorecardpinned?: Partial(string) & Partial(null)
  scorecardscore?: Partial(string) & Partial(null)
  binaryartifacts?: Partial(string) & Partial(null)
  branchprotection?: Partial(string) & Partial(null)
  ciibestpractices?: Partial(string) & Partial(null)
  codereview?: Partial(string) & Partial(null)
  dangerousworkflow?: Partial(string) & Partial(null)
  fuzzing?: Partial(string) & Partial(null)
  license?: Partial(string) & Partial(null)
  maintained?: Partial(string) & Partial(null)
  packaging?: Partial(string) & Partial(null)
  pinneddependencies?: Partial(string) & Partial(null)
  sast?: Partial(string) & Partial(null)
  securitypolicy?: Partial(string) & Partial(null)
  signedreleases?: Partial(string) & Partial(null)
  tokenpermissions?: Partial(string) & Partial(null)
  vulnerabilities?: Partial(string) & Partial(null)
}
```

### #/components/schemas/HTTPValidationError

```typescript
{
  detail: {
    loc?: Partial(string) & Partial(integer)[]
    msg: string
    type: string
  }[]
}
```

### #/components/schemas/StatusMsg

```typescript
{
  status?: string
  service_name?: string
}
```

### #/components/schemas/ValidationError

```typescript
{
  loc?: Partial(string) & Partial(integer)[]
  msg: string
  type: string
}
```
