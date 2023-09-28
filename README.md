# Runit CLI ![Python](https://img.shields.io/badge/builthwith-python-brightgreen) 
The Runit Command Line Interface (CLI) Tools can be used to test, manage, and deploy your Runit project from the command line.
- Create new runit project
- Run a local web server for your runit project
- publish code and assets to your runit-server domain
- Interact with data in your runit-server database


## Supported Languages
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54) ![JavaScript](https://img.shields.io/badge/javascript-%23323330.svg?style=for-the-badge&logo=javascript&logoColor=%23F7DF1E) ![PHP](https://img.shields.io/badge/php-%23777BB4.svg?style=for-the-badge&logo=php&logoColor=white)

## Installation
### Python Package
You can install the Runit CLI using pip (Python package manager). Note that you will need to install [Python](https://python.org).
To download and install the runit CLI run the following command:
```shell
pip install runit
```
This will provide you with the globally accessible ```runit``` command.

### Install from source
```shell
git clone https://github.com/theonlyamos/runit.git
cd runit
pip install .
```

## Usage
Run the below command to print out usage message.
```shell
runit --help
```
![Runit Cli](https://awesomescreenshot.s3.amazonaws.com/image/3778408/34500895-ad63d3ceaef8002f59fc5fd499797ca5.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIAJSCJQ2NM3XLFPVKA%2F20221117%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Date=20221117T180652Z&X-Amz-Expires=28800&X-Amz-SignedHeaders=host&X-Amz-Signature=afd652759d272e68a62fb9959ce4e86647af5d6269991c012c9e753bf22ef534)

**Create New Project**
Run the following in the command line to create a new runit project.
> Supported languages include: [Python](), [Javascript](), [PHP]()
```shell
runit new <project-name> --language <langugage>
```
Run ```runit new --help``` for all options

**Run project locally**
***Access functions on local server****
Running the command ```runit``` in a project directory spins up a local webserver which can be used to access the funtions in project.
```shell
cd <project-directory>
runit
```
Point your browser to the address provided followed by the function name to access that function.
```http://localhost:5000/``` will be the default address.
Visiting ```http://localhost:5000/hello_world``` will run the ```hello_world``` function in the project.

***Run function and print output to shell***
Output function result to shell. Required arguments include:
> ```--function <function_name>```: Function name to call
> ```--shell```: sets shell output to true
> [Optional] ```--arguments|-x```: Arguments for the function if required. Can be called multiple times for multiple arguments

```shell
cd <project-directory>
runit --function <hello_world> --shell
```

### Publishing Project
Before you can publish any of your projects, you must setup the backend for your runit. You must also be logged in.

**Setup Backend Details**
The backend must be running ***[runit-server](https://github.com/theonlyamos/runit-server)***.
Run ```runit setup --help``` for help message.
***Follow the prompts to complete the setup after running the below comman.***
```shell
runit setup
```

**Account Login**
```shell
runit login --help
```
```shell
runit login --email <email@example.org> --password <supersecretpass>
```
**or**
***Follow the commands after running below command***
```shell
runit login
```

**Deploy/Publish Project**
```shell
cd <project-directory>
runit publish
```

## License
![License](https://img.shields.io/badge/LICENSE-MIT-brightgreen/?style=flat-square)

**Free Software, Hell Yeah!**

