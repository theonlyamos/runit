
<div align="center">
<h1 align="center">
<img src="https://raw.githubusercontent.com/PKief/vscode-material-icon-theme/ec559a9f6bfd399b82bb44393651661b08aaf7ba/icons/folder-markdown-open.svg" width="100" />
<br>
runit
</h1>
<h3 align="center">📍 Runit with GitHub: Code Your Way to Success!</h3>
<h3 align="center">🚀 Developed with the software and tools below:</h3>
<p align="center">

<img src="https://img.shields.io/badge/JSON-000000.svg?style=for-the-badge&logo=JSON&logoColor=white" alt="JSON" />
<img src="https://img.shields.io/badge/HTML5-E34F26.svg?style=for-the-badge&logo=HTML5&logoColor=white" alt="HTML5" />
<img src="https://img.shields.io/badge/Markdown-000000.svg?style=for-the-badge&logo=Markdown&logoColor=white" alt="Markdown" />
<img src="https://img.shields.io/badge/MySQL-4479A1.svg?style=for-the-badge&logo=MySQL&logoColor=white" alt="MySQL" />
<img src="https://img.shields.io/badge/Jinja-B41717.svg?style=for-the-badge&logo=Jinja&logoColor=white" alt="Jinja" />

<img src="https://img.shields.io/badge/Python-3776AB.svg?style=for-the-badge&logo=Python&logoColor=white" alt="Python" />
<img src="https://img.shields.io/badge/JavaScript-F7DF1E.svg?style=for-the-badge&logo=JavaScript&logoColor=black" alt="JavaScript" />
<img src="https://img.shields.io/badge/PHP-777BB4.svg?style=for-the-badge&logo=PHP&logoColor=white" alt="PHP" />
<img src="https://img.shields.io/badge/Flask-000000.svg?style=for-the-badge&logo=Flask&logoColor=white" alt="Flask" />
<img src="https://img.shields.io/badge/Gunicorn-499848.svg?style=for-the-badge&logo=Gunicorn&logoColor=white" alt="Gunicorn" />
</p>

</div>

---

## 📚 Table of Contents
- [📚 Table of Contents](#-table-of-contents)
- [📍Overview](#-introdcution)
- [🔮 Features](#-features)
- [⚙️ Project Structure](#project-structure)
- [🧩 Modules](#modules)
- [🏎💨 Getting Started](#-getting-started)
- [🗺 Roadmap](#-roadmap)
- [🤝 Contributing](#-contributing)
- [🪪 License](#-license)
- [📫 Contact](#-contact)
- [🙏 Acknowledgments](#-acknowledgments)

---


## 📍Overview

Runit CLI provides an open-source command line interface which enables developers to rapidly create, deploy, and manage serverless applications using Python, JavaScript, and PHP. It also provides tools to interact with data in a Runit server database. This makes it easier for developers to build and deploy applications quickly, while also giving them flexibility to customize their applications to meet their specific needs. The Runit CLI is a valuable tool for developers, as it simplifies complex tasks and reduces development time.

---

## 🔮 Feautres

### Distinctive Features

1. **User-Centered Design Elements and Architecture:** Runit utilizes a user-centered design, allowing for the creation of serverless applications that are easy to interact with and deploy. It also provides tools to create new projects, run a local web server, publish code and assets, and interact with data in a runit server database.
2. **Multi-Language Support:** Runit supports multiple programming languages, including Python, JavaScript, and PHP. It provides specialized functions and tools for each language, as well as a runtime environment and a class for parsing and running functions from a file.
3. **Flexible Templates:** Runit provides pre-made templates for each language, containing functions for printouts, counting, getting the current time, and selecting a random quote. It also includes a 404 error page with an eye-catching design and Normalize CSS styling.
4. **Account Management:** Runit has a set of methods to manage user accounts, allowing for user registration and login, authentication, project creation and deletion, and more. It also provides a way to store and retrieve access tokens.

---


<img src="https://raw.githubusercontent.com/PKief/vscode-material-icon-theme/ec559a9f6bfd399b82bb44393651661b08aaf7ba/icons/folder-github-open.svg" width="80" />

## ⚙️ Project Structure




---

<img src="https://raw.githubusercontent.com/PKief/vscode-material-icon-theme/ec559a9f6bfd399b82bb44393651661b08aaf7ba/icons/folder-src-open.svg" width="80" />

## 💻 Modules

<details closed><summary>Root</summary>

| File           | Summary                                                                                                                                                                                                                                                                                                                                                                                                                  | Module                                |
|:---------------|:-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:--------------------------------------|
| PKG-INFO       | Runit CLI is an open-source command line interface for developing and deploying serverless applications using Python, JavaScript, and PHP. It provides tools to create new projects, run a local web server, publish code and assets, and interact with data in a runit server database. Install the CLI using pip and use the "runit" command to print out usage messages. Runit CLI is licensed under the MIT License. | python_runit.egg-info\PKG-INFO        |
| .flaskenv      | This code script sets up an environment for a Flask application with development mode enabled and debugging enabled, as well as setting the application port to 9000.                                                                                                                                                                                                                                                    | runit\.flaskenv                       |
| cli.py         | Error generating file summary.                                                                                                                                                                                                                                                                                                                                                                                           | runit\cli.py                          |
| constants.py   | This code script imports the dotenv library, specifies various variables for versioning, file names, and language extensions, defines loaders and runners for the different languages, and sets up the runtime environment. It then sets up a dictionary for the base HTTP headers.                                                                                                                                      | runit\constants.py                    |
| favicon.ico    | This code script is unable to decode content which is not text or which is not encoded in the UTF-8 format.                                                                                                                                                                                                                                                                                                              | runit\favicon.ico                     |
| Procfile       | This code script runs a web server using the Gunicorn application, connecting it to the'app' application.                                                                                                                                                                                                                                                                                                                | runit\Procfile                        |
| Request.py     | This code script creates and manages a Request class to retrieve and parse data from a server. It initializes with an HTTP GET request, stores the response as parameters, and provides methods to access GET and POST data from the response.                                                                                                                                                                           | runit\Request.py                      |
| runit.py       | Error generating file summary.                                                                                                                                                                                                                                                                                                                                                                                           | runit\runit.py                        |
| test.py        | This code script contains three functions:'multiply' multiplies numbers,'add' adds numbers, and'minus' subtracts num2 from num1. All three functions require parameters and print the result, but do not return a value.                                                                                                                                                                                                 | runit\test.py                         |
| javascript.py  | This code script imports the'Runtime' module and defines the'Javascript' class for parsing and running Javascript functions from a file. It also specifies the'LOADER' and'RUNNER' paths within the'tools/javascript' directory. The'__init__' method inherited from the'Runtime' class is also utilized.                                                                                                                | runit\languages\javascript.py         |
| multi.py       | This code script contains a class,'Multi', for parsing and running python functions from a file. It includes methods for loading files and exported functions from supported file types, as well as a method for listing functions and an anonymous function for running functions with arguments.                                                                                                                       | runit\languages\multi.py              |
| php.py         | This code script imports an OS module and a Runtime class. It then defines a PHP_TOOLS_DIR and a PHP class which extends Runtime and contains two variables for loading and running php functions from a file. It also contains an __init__ function which calls the super() method of Runtime.                                                                                                                          | runit\languages\php.py                |
| python.py      | This code script creates a Python class which is a subclass of the Runtime class. It sets two constants, LOADER and RUNNER, to the filepaths of two Python tools, and provides a constructor for initializing the class.                                                                                                                                                                                                 | runit\languages\python.py             |
| runtime.py     | This code script creates a class for parsing and running functions from a file. It allows the user to define a filename and the associated runtime, with support for multiple file extensions. It also allows for functions to be loaded from the file and provides methods for listing the functions and running them with arguments.                                                                                   | runit\languages\runtime.py            |
| account.bak    | This code script provides a way to access a token with a value of 313.                                                                                                                                                                                                                                                                                                                                                   | runit\modules\account.bak             |
| account.dat    | This code script prevents content from being decoded if it is not a text file or encoded with UTF-8.                                                                                                                                                                                                                                                                                                                     | runit\modules\account.dat             |
| account.dir    | This code script retrieves an access token with a value of 0-313.                                                                                                                                                                                                                                                                                                                                                        | runit\modules\account.dir             |
| account.py     | This code script provides a set of methods to manage user accounts. It allows for user registration and login, as well as the ability to authenticate the user, retrieve account information, create and delete projects, clone existing projects, and retrieve and update functions. It also provides a static method to load and store access tokens.                                                                  | runit\modules\account.py              |
| .runitignore   | This code script includes directories for virtual environment, node modules, and vendor, as well as files for package-lock and composer-lock.                                                                                                                                                                                                                                                                            | runit\templates\.runitignore          |
| 404.html       | This code script creates an error page with an eye-catching 404 Not Found message, including a Pacifico font and accompanying image, centered on a page with Normalize CSS styling.                                                                                                                                                                                                                                      | runit\templates\404.html              |
| main.js        | This code script provides four functions to be exported, such as'index' which logs'Yay, Javascript works!!!','counter' which logs a sequence of numbers,'printout' which logs a given string and'time' which logs the current date and time.                                                                                                                                                                             | runit\templates\javascript\main.js    |
| application.py | This code script imports the request package and implements various functions such as index(), counter(), printout(), time() and quote() to print out a quote from a list of famous quotes and a timestamp of the current UTC time.                                                                                                                                                                                      | runit\templates\multi\application.py  |
| index.php      | This script contains four functions that enable the output of strings and numerical values, as well as the current date and time.                                                                                                                                                                                                                                                                                        | runit\templates\multi\index.php       |
| main.js        | This code script exports four functions: index, counter, printout, and time. Index logs a celebratory message, counter logs a list of numbers, printout logs a given string, and time logs the current time.                                                                                                                                                                                                             | runit\templates\multi\main.js         |
| request.php    | This code script uses cURL to connect to a server, retrieve an application request, and set the retrieved data as GET and POST variables.                                                                                                                                                                                                                                                                                | runit\templates\multi\request.php     |
| test.php       | This code script prints the string "Text PHP" to the screen using PHP.                                                                                                                                                                                                                                                                                                                                                   | runit\templates\multi\test.php        |
| index.php      | This code script contains four functions that print out strings and a date string:'Yay, PHP works!!!', a string variable,'1,2,3,4,5', and the current date and time in the format'Y-m-d H:i:s'.                                                                                                                                                                                                                          | runit\templates\php\index.php         |
| request.php    | This code script initializes a cURL call to an endpoint to retrieve application requests, then decodes the result into an array and sets the local $_GET and $_POST variables to the values from the array.                                                                                                                                                                                                              | runit\templates\php\request.php       |
| test.php       | This code script uses the PHP language to output the string "Text PHP".                                                                                                                                                                                                                                                                                                                                                  | runit\templates\php\test.php          |
| application.py | This code script imports the request package and provides a range of functions for printouts, counting, getting the current time, and selecting a random quote.                                                                                                                                                                                                                                                          | runit\templates\python\application.py |

</details>

<hr />

## 🚀 Getting Started

### ✅ Prerequisites

Before you begin, ensure that you have the following prerequisites installed:
> `[📌  INSERT-PROJECT-PREREQUISITES]`

### 💻 Installation

1. Clone the runit repository:
```sh
git clone C:/Users/Ph4n70m/Workspace/python/runit
```

2. Change to the project directory:
```sh
cd runit
```

3. Install the dependencies:
```sh
pip install -r requirements.txt
```

### 🤖 Using runit

```sh
python main.py
```

### 🧪 Running Tests
```sh
#run tests
```

<hr />


## 🛠 Future Development
- [X] [📌  COMPLETED-TASK]
- [ ] [📌  INSERT-TASK]
- [ ] [📌  INSERT-TASK]


---

## 🤝 Contributing
Contributions are always welcome! Please follow these steps:
1. Fork the project repository. This creates a copy of the project on your account that you can modify without affecting the original project.
2. Clone the forked repository to your local machine using a Git client like Git or GitHub Desktop.
3. Create a new branch with a descriptive name (e.g., `new-feature-branch` or `bugfix-issue-123`).
```sh
git checkout -b new-feature-branch
```
4. Make changes to the project's codebase.
5. Commit your changes to your local branch with a clear commit message that explains the changes you've made.
```sh
git commit -m 'Implemented new feature.'
```
6. Push your changes to your forked repository on GitHub using the following command
```sh
git push origin new-feature-branch
```
7. Create a pull request to the original repository.
Open a new pull request to the original project repository. In the pull request, describe the changes you've made and why they're necessary.
The project maintainers will review your changes and provide feedback or merge them into the main branch.

---

## 🪪 License

This project is licensed under the `[📌  INSERT-LICENSE-TYPE]` License. See the [LICENSE](https://docs.github.com/en/communities/setting-up-your-project-for-healthy-contributions/adding-a-license-to-a-repository) file for additional info.

---

## 🙏 Acknowledgments

[📌  INSERT-DESCRIPTION]


---

