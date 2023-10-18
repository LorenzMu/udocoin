# Setup blockchain API

To ensure same versions on development devices and Docker Images

## Init virtual environment

```sh
cd udocoin_miner
```

```sh
python -m venv venv
```

## Activate virtual environment

Windows cmd

```sh
venv\Scripts\activate.bat
```

Windows PowerShell

```sh
venv\Scripts\activate.ps1
```

If error: "... cannot be loaded because the execution of scripts is disabled on this system.", enable execution with

```sh
Set-ExecutionPolicy RemoteSigned
```

## Install requirements

```sh
pip install -r requirements.txt
```

## update requirements

```sh
pipreqs --force
```

## deactivate virtual environment

```sh
deactivate
```