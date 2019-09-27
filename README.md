<p align="center">
  <a href="" rel="noopener">
 <img width=200px height=200px src="https://raw.githubusercontent.com/jayfk/launchr/master/logo.png" alt="Launchr"></a>
</p>

<h3 align="center">Launchr</h3>

<div align="center">

  [![Status](https://img.shields.io/badge/status-active-success.svg)]() 
  [![GitHub Issues](https://img.shields.io/github/issues/jayfk/launchr.svg)](https://github.com/kylelobo/The-Documentation-Compendium/issues)
  [![GitHub Pull Requests](https://img.shields.io/github/issues-pr/jayfk/launchr.svg)](https://github.com/kylelobo/The-Documentation-Compendium/pulls)
  [![License](https://img.shields.io/badge/license-MIT-blue.svg)](/LICENSE)

</div>

---

<p align="center"> 
    Launchr is an open source SaaS starter kit.<br> 
</p>

## Getting Started <a name = "getting_started"></a>
Launchr is at a very early stage. If you want to try it out, follow the examples below.

### Prerequisites
Install [Docker](https://docs.docker.com/install/) and [Docker Compose](https://docs.docker.com/compose/install/).

### Installing
Generate a new project in your current working directory by running
```
docker run --rm -it -v ${PWD}:/out jayfk/launchr
```

Start up the stack with
```
docker-compose -f local.yml up
```
