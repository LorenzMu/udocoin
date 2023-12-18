# udocoin

A Blockchain-project as part of the class "Distributed Systems" in the winter semester 2023 of the course TINF21AI2 at DHBW Mannheim.

## Contributors

| Name | Matrikel number |
| --- | --- |
| Matthias Heilmann | 4186046 |
| Lorenz Müller | 8350586 |
| Sean Schwarz | 3446064 |
| Leo Stadtler | 9230282 |

# Guides

The following paragraphs explain how to run the miner-application and the wallet app

## Udocoin Miner

### Docker/docker-compose

To run the udocoin miner application, with Docker you need to have Docker Desktop and docker-compose installed on your machine. 

If you don't have a public and a private key, you also need to have at least python 3.8 to generate keys. (See References for testing keys)

In your terminal, change your directory to udocoin/udocoin_miner

```sh
cd udocoin_miner
```

Execute the start files and follow the instructions in the terminal.

Windows:
```sh
start.ps1
```

Other operating systems:
```sh
source start.sh
```

Building the docker containers will take some time. Keep in mind to have the Docker Desktop app running while building the application.

The server will be running on [localhost:80](http://localhost).

### Without Docker

To run the udocoin miner application without Docker, you need to have at least python 3.8 installed.

Change the directory to udocoin/udocoin_miner/application

```sh
cd udocoin_miner/application
```

Create and activate a python virtual environment and install required packages

Windows:

```sh
python -m venv venv
venv\Scripts\activate.ps1
pip install -r requirements.txt
```

Other operation systems:

```sh
python3 -m venv venv
source venv/Scripts/activate
pip3 install -r requirements.txt
```

And then start the server

Windows:

```sh
python run.py
```

Other operating systems:

```sh
python3 run.py
```

Follow the instructions in the terminal and the server will be running on [localhost:5000](http://localhost:5000).

## Udocoin Wallet

To create and send transactions the wallet app must be used. You can download the APK-File [here](https://drive.google.com/file/d/1yusORkja0yB-bQkYlmvke-RJx2j43PTV/view?usp=drive_link) and install it on you android device with an android version of at least 7.1.1. It is recommended to use a USB-cable to transfer the app to the mobile device.

The app was developed and tested on 

* Google Pixel 3a (Android version 13)
* Samsung Galaxy A52 (Android version 13)

If there are problems with the installation of the APK-file, try to open the project in Android Studio to run the development version.

The app will notify you that it's running with an unlicensed version of Ch

# References

| Name | Link |
| --- | --- |
| Primary GitHub Repository | https://github.com/LorenzMu/udocoin |
| Thesis |  |
| Wallet-app APK | https://drive.google.com/file/d/1yusORkja0yB-bQkYlmvke-RJx2j43PTV/view?usp=drive_link |
| Sources gDrive | https://drive.google.com/drive/folders/1zLEWjr3jMXuw4lIt8uKNWesUSG-uYkJ3 |
