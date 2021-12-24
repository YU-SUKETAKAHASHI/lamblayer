# lamblayer

lamblayer is a minimal deployment tool for AWS Lambda layers.

lamblayer does,
- Create a Layers of built pip-installable python packages.
- Create a Layers from local directory.
- Update function Layers.

That's all.

## Install
### pip
```
$ pip install git+https://github.com/YU-SUKETAKAHASHI/lamblayer.git@v0.1.0
```

### Github Actions
```yaml
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: YU-SUKETAKAHASHI/lamblayer@v0
        with:
          version: v0.1.0
      - run: |
          lamblayer set

```

## Quick start
Try migrate your existing Lambda function quick_start.
```
$ mkdir quick_start
$ cd quick-start
$ lamblayer init --function-name quick_start
2021-12-24 10:13:41,225: [INFO]: lamblayer : v0.1.0
2021-12-24 10:13:42,132: [INFO]: starting init quick_start
2021-12-24 10:13:42,318: [INFO]: createing function.json
2021-12-24 10:13:42,319: [INFO]: completed
```

Now you can set layer to quick_start fuction using `lamblayer set`.
```
$ lamblayer set
2021-12-24 10:23:34,041: [INFO]: lamblayer : v0.3.0
2021-12-24 10:23:35,312: [INFO]: starting set layers to quick_start
2021-12-24 10:23:35,723: [INFO]: completed
```



## Usage
```
Usage: lamblayer [OPTIONS] COMMAND [ARGS]...

  lamblayer : v0.1.0

  lamblayer is a minimal deployment tool for AWS Lambda Layers.

Options:
  --profile TEXT                  AWS credential profile
  --region TEXT                   AWS region
  --log-level [DEBUG|INFO|WARNING|ERROR|CRITICAL]
                                  log level  [default: (INFO)]
  --help                          Show this message and exit.

Commands:
  create   create a layer.
  init     initialize function.json
  list     show list of the layers.
  set      set layers to function.
  version  show lamblayer's version number.
```

### Init
`Init`ialize `set_layer.json` by existing function.
```
Usage: lamblayer init [OPTIONS]

  initialize function.json

Options:
  --profile TEXT                  AWS credential profile
  --region TEXT                   AWS region
  --log-level [DEBUG|INFO|WARNING|ERROR|CRITICAL]
                                  log level
  --function-name TEXT            function name for initialize  [default:
                                  LAMBLAYER]
  --download                      download all layers.zip, or not  [default:
                                  False]
  --help                          Show this message and exit.
```
`lamblayer init` create `set_layer.json` as a configration file for layers of the function.
```
lamblayer init --function-name your_function_name
```
If `--download` is selected, download all layer zip contents at `./{layer_name}-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx.zip`


### Create
`Create` a layer of built pip-installable python packages, or from local directory.
```
Usage: lamblayer create [OPTIONS]

  create a layer.

Options:
  --profile TEXT                  AWS credential profile
  --region TEXT                   AWS region
  --log-level [DEBUG|INFO|WARNING|ERROR|CRITICAL]
                                  log level
  --packages TEXT                 packages file path  [default:
                                  (packages.json)]
  --src TEXT                      a root directory to put in the layer.
                                  [default: (.)]
  --wrap-dir1 TEXT                a wrap directory1 name
  --wrap-dir2 TEXT                a wrap directory2 name
  --layer TEXT                    layer config file  [default: layer.json]
  --help                          Show this message and exit.
```
1. pip-installable packages

Creating a layer of pip-installable python packages, spesify packages config file with `--packages`, and layer config file with `--layer`.

```
lamblayer create --packages packages.json --layer layer.json
```


2. from local directory

Creating a layer from local directory, spesify src directory with `--src`, and layer config file with `--layer`.

```
lamblayer create --src my_packages --layer.json
```

In layers, you have to place script files in the `python` directory, but lamblayer can handle the placing for you.
You can wrap your package using `--wrap-dir1` and `--wrap-dir2`.

ex1）

your dir tree,
```
.
├── layer.json
└── my_package
    ├── __init__.py
    ├── module1.py
    └── module2.py

```
command,
```
lamblayer create --src my_package --wrap-dir1 python
```

now, created layer dir tree.
```
python
├── __init__.py
├── module1.py
└── module2.py
```

ex2）

your dir tree,
```
.
├── layer.json
└── my_package
    ├── __init__.py
    ├── module1.py
    └── module2.py

```

command,
```
lamblayer create --src my_package --wrap-dir1 python --wrap-dir2 my_package
```

now, created layer dir tree.
```
python
└── my_package
    ├── __init__.py
    ├── module1.py
    └── module2.py
```


### packages.json
packages.json is a difinition for [LayerZip]().
These attributes will be used for LayerZip API call.
```json
{
    "Arch": "x86_64",
    "Runtime": "py39",
    "Packages": [
        "numpy==1.20.2",
        "requests"
    ]
}
```
`Arch` (string):
the instruction set architecture you want for your function code. [`x86_64` | `arm64`]

`Runtime` (string):
the language of your lambda that uses this layer. [`py37` | `py38` | `py39`]

`Packages` (list, string):
the pip-installable packages name. You can specify version of package in the same way as pip install.



### layer.json
layer.json is a definition for Lambda layers. JSON structure is based from [`PublishLayerVersion` for Lambda API](https://docs.aws.amazon.com/lambda/latest/dg/API_PublishLayerVersion.html).
```json
{
    "LayerName": "numpy_requests",
    "Description": "numpy==1.20.2, requests",
    "CompatibleRuntimes": [
        "python3.7",
        "python3.8",
        "python3.9"
    ],
    "LicenseInfo": ""
}
```

### Set
`Set` layers to the function.
```
Usage: lamblayer set [OPTIONS]

  set layers to function.

Options:
  --profile TEXT                  AWS credential profile
  --region TEXT                   AWS region
  --log-level [DEBUG|INFO|WARNING|ERROR|CRITICAL]
                                  log level
  --function TEXT                 function config file  [default:
                                  function.json]
  --help                          Show this message and exit.
```
`lamblayer set` changes the configration of the function for layers.

```
lamblayer set --set-layer set_layer.json
```

### function.json
function.json is a definition for Lambda function. JSON structure is part of [`CreateFunction` for Lambda API](https://docs.aws.amazon.com/lambda/latest/dg/API_CreateFunction.html).
```json
{
    "FunctionName": "lamblayer",
    "Layers": [
        "arn:aws:lambda:ap-northeast-1:xxxxxxxxxxxx:layer:Galaxy:42",
        "lamblayer_layer"
    ]
}

```

If the name of layer is only passed, completes it to the ARN(Amazon Resourse Name) with the latest version number.

`ex) arn:aws:lambda:{your_region}:{your_accountid}:layer:lambdarider_layer:{latest_version_number}`


### List
Show `List` of the layers.
```
Usage: lamblayer list [OPTIONS]

  show list of the layers.

Options:
  --profile TEXT                  AWS credential profile
  --region TEXT                   AWS region
  --log-level [DEBUG|INFO|WARNING|ERROR|CRITICAL]
                                  log level
  --help                          Show this message and exit.
```

```
lamblayer list
```

## LICENSE
MIT License

Copyright© 2021 Yusuke Takahashi