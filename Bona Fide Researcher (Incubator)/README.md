# Bona Fide Researcher

```
      |
  \  ___  /                           _________
 _  /   \  _    GÉANT                 |  * *  | Co-Funded by
    | ~ |       Trust & Identity      | *   * | the European
     \_/        Incubator             |__*_*__| Union
      =
```

## About

This is an implementation of an experimental verification tool for researcher identity. It was
developed as a part of the GÉANT Trust & Identity Incubator.

The main purpose of this project is to provide a simple tool, primarily intended for academic
journal editors, who need to verify the identity of the researchers attempting to publish their
academic works.

This tool is a purely backend component that can be used directly from the command line interface (
CLI). Alternatively, it provides a simple Flask application that is able to expose the functionality
through an API. This allows for integration with other systems. One such example is the Bona Fide
OJS plugin.

## Functionality

The functionality consists of the following parts:

### Researcher verification

This module serves the purpose of gathering publicly available data about the researcher, joining
them into a concise report and presenting the results as a ranked list of candidate identities based
on internal confidence metrics. The information sources about the researchers are:

- [arXiv](https://arxiv.org/) - free distribution service and an open-access archive for scholarly
  articles
- [Crossref](https://search.crossref.org/) - digital infrastructure for scholarly metadata
  aggregation and lookup
- [EOSC Resource hub](https://open-science-cloud.ec.europa.eu/resources/all) -
- [ORCID](https://orcid.org/) - system for identification and lookup of authors and their
  bibliographic output
- [ROR (Research Organization Registry)](https://ror.org/) - global, community-led registry of open
  persistent identifiers for research organizations

This functionality can be used to help build a more complete picture about an academic person's
identity and presence in the research world from publicly available data. For example, journal
editors who often receive just an author's name may use it to quickly extract more information to
back up their confidence in the author's claimed identity.

### Researcher's collaboration network inspection

This module uses the [arXiv API](https://info.arxiv.org/help/api/) to gather researcher's
publication data and extract their co-authors. It can then crawl the network of co-authors to a
requested depth (the default is one level) and look for their co-authors. This way, a network of
author's direct and indirect connections in the academic publications can be built.

The use cases for this functionality can vary between a practical search for potential
collaborators, searching for fraud attempts or conflicts of interests where colleagues review each
other's articles.

## Usage

Researcher verification script can be invoked in two ways:

### Command-line interface (CLI)

The verification tool is a Python script found in the root directory of the project in
`verify_eduperson.py`. It can be run by executing the command:

`python3 verify_eduperson.py -gn John -sn Doe`

The following table describes the arguments usable with this script:

```aiignore
|----------------------------|----------|-----------------------------------------------------------------------------------------------------------------------------------|
| Argument                   | Required | Description                                                                                                                       |
|----------------------------|----------|-----------------------------------------------------------------------------------------------------------------------------------|
| -h, --help                 | No       | show this help message and exit                                                                                                   |
| -gn, --given-name          | Yes      | Given name of the person to be verified                                                                                           |
| -sn, --surname             | Yes      | Surname of the person to be verified                                                                                              |
| -e, --email                | No       | Email address of the person to be verified                                                                                        |
| -o, --orcid                | No       | ORCID identifier of the person to be verified                                                                                     |
| -a, --affiliation          | No       | (Institutional) Affiliation of the person to be verified (ROR, ISNI or name)                                                      |
| -l, --limit-results        | No       | Limit the output results to first N by rank                                                                                       |
| -u, --uncertain-name-order | No       | Add when uncertain which name is the given name and which is the surname. Given name and Surname will be treated interchangeably. |
| -v, --verbose              | No       | When present, all the available information about the researcher will be shown.                                                   |
| -d, --verify-email-domain  | No       | When present, email domain will be verified through ROR. Email must be provided.                                                  |
|----------------------------|----------|-----------------------------------------------------------------------------------------------------------------------------------|
```

### API

The researcher verification functionality can also be exposed using an API hosted by a simple Flask
application. This can serve as a backend that provides the researcher data in a structured JSON
format that can be visually presented on the frontend.

The application can be launched in a Docker container using the included Dockerfile in the root directory. One way to do this is:

 1. [install Docker](https://www.docker.com/get-started/)
 2. in the terminal, run: `docker build -t bona_fide_app:latest .` to build the docker image
 3. launch a container by running: `docker run -p 8000:5000 bona_fide_app:latest` (by default, the app runs on port 8000 and Dockerfile exposes port 5000)
This container exposes the API endpoints on port 5000.Do

#### Endpoints:

As request processing can take a longer time. Therefore, the response to an API request is deferred, and it can be obtained in two ways:
 1. You provide a `callback_url` among the request arguments. The request is processed asynchronously and a response is returned to the `callback_url`. This is a form of passive waiting for the response.
 2. Calling an API request returns a response to the caller containing a `job_id`, `job_status`, a `message` explaining how to handle the response and a `researchers_name` to get a human-readable identification of the request if multiple researchers are queried at a time. Example response:  
    ```aiignore
    {
            "job_id": "6aa301d0-3592-4041-b035-1f5c4bee8788",
            "message": "Your job has been submitted and assigned an ID: 6aa301d0-3592-4041-b035-1f5c4bee8788. Please wait for the response on the callback URL: https://my.site/callback. You can track the progress of the job by calling the status endpoint:  /status/<job_id>",
            "researcher_name": "John Doe",
            "status": "RUNNING"
    }
    ```
    The `/status/<job_id>` endpoint can then be actively polled with the `job_id` in the url query parameter to obtain the status of the job or the result itself if the job is finished.

`/verify-eduperson`
- purpose: get researcher's identity data, equivalent to `verify_eduperson.py` in [CLI](#command-line-interface-cli)
  - method: `GET`
  - arguments:
    - passed inside a JWT token in the Authorization header as Bearer auth in the request
    - the JWT sent in the request **must** be signed with HS256 algorithm using the signing key configured in `configs/config.py` as `jwt_secret_key` 
    - query arguments are the same as in the [CLI version](#command-line-interface-cli) with one extra required argument: `callback_url`
      - a single researcher can be queried in format:
        ```aiignore
          {
                "given_name": "John",
                "surname": "Doe",
                "email": "john.doe@uni.org",
                "limit_results": 5,
                "uncertain_name_order": true,
                "verify_email_domain": true,
                "callback_url": "https://my.site/callback"
          }
          ```
      - multiple researchers at a time can be queried in format:
        ```aiignore
          {
            "researchers": [
              {
                "given_name": "Stephen",
                "surname": "Hawking",
                "callback_url": "https://my.site/callback"
              },
              {
                "given_name": "Kip",
                "surname": "Thorne",
                "callback_url": "https://my.site/callback
              }
            ]
          }
          ```
  - example usage:
    - HTTP GET request: http://127.0.0.1:8000/verify-eduperson
      - request Authorization header: `"Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJnaXZlbl9uYW1lIjoiSm9obiIsInN1cm5hbWUiOiJEb2UiLCJlbWFpbCI6ImpvaG4uZG9lQHVuaS5vcmciLCJsaW1pdF9yZXN1bHRzIjo1LCJ1bmNlcnRhaW5fbmFtZV9vcmRlciI6dHJ1ZSwidmVyaWZ5X2VtYWlsX2RvbWFpbiI6dHJ1ZSwiY2FsbGJhY2tfdXJsIjoiaHR0cHM6Ly9teS5zaXRlL2NhbGxiYWNrIn0.OfNqxtMPX2KocEvQTAg11oKU_LK-FmE3chUB5Xa0hXk"`

`/status/<job_id>`
  - purpose: get researcher's identity data, equivalent to verify_eduperson.py in CLI
  - method: `GET`
  - arguments: `job_id` returned in the response to a request
  - example usage:
    - HTTP GET request: http://127.0.0.1:8000/status/6aa301d0-3592-4041-b035-1f5c4bee8788

Researcher's collaboration network script is accessible only through the API. The principles of the deferred response are the same as in the [eduperson verificaiton](#endpoints). The caller has to provide the `callback_url` in the request, and they can decide whether to await the result at the callback url or actively poll the status endpoint with the job id. 

### Endpoints

`/researcher-relationship-graph`
- purpose: get the network of researchers who have been listed as the target's co-authors up to a specified depth
- method: `GET`
- arguments:
  - passed inside a JWT token in the Authorization header as Bearer auth in the request
  - `full_name` - full name of the researcher for whom the network is constructed
  - `callback_url` - url where the result is returned after the query has been processed (required)
  - `max_relationship_depth` - depth of the network → 1 = direct co-authors, 2 = co-authors of co-authors etc.  (not required, default is set in `configs/config.py` by `max_relationship_depth_default`)
  
- a single researcher can be queried in format:
```aiignore
{
      "full_name": "John Doe",
      "max_relationship_depth": 3,
      "callback_url": "https://my.site/callback"
}
```
    
- multiple researchers at a time can be queried in format:
```aiignore
{
  "researchers": [
    {
      "full_name": "Stephen Hawking",
      "max_relationship_depth": 2,
      "callback_url": "https://my.site/callback"
    },
    {
      "full_name": "Kip Thorne",
      "callback_url": "https://my.site/callback"
    }
  ]
}
```
- example usage:
    - HTTP GET request: http://127.0.0.1:8000/researcher-relationship-graph
      - request Authorization header: `"Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJyZXNlYXJjaGVycyI6W3siZnVsbF9uYW1lIjoiU3RlcGhlbiBIYXdraW5nIiwibWF4X3JlbGF0aW9uc2hpcF9kZXB0aCI6MiwiY2FsbGJhY2tfdXJsIjoiaHR0cHM6Ly9teS5zaXRlL2NhbGxiYWNrIn0seyJmdWxsX25hbWUiOiJLaXAgVGhvcm5lIiwiY2FsbGJhY2tfdXJsIjoiaHR0cHM6Ly9teS5zaXRlL2NhbGxiYWNrIn1dfQ.JnWGgDy6JqHqt7YsFDX5v6fGZCZewrEsb6ZJYZ793Ns`

## Related projects
This backend contains and integrates with other components developed as parts of the GÉANT Trust & Identity Incubator. The ROR module for email domain verification and researcher's collaboration network inspection tools are accessible in this [GitHub repository](https://github.com/JovanSimonoski/GEANT-TIM-BonaFide). This backend is also integrated in the [Bona Fide Plugin](https://github.com/alexarlord-boop/bona-fide-ojs) for [OJS](https://openjournalsystems.com/). This serves as a practical demonstration of the utility of this module when integrated in a suitable environment.