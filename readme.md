# Task Management System
Web application for managing tasks.
## Usage
First you need to create a virtual environment and install dependencies:
```bash
python -m venv venv
```
```bash
source venv/bin/activate
```
```bash
pip install -r requirements.txt
```
Then you need to migrate the database:
```bash
python manage.py migrate
```
Then you can run the application:
```bash
python manage.py runserver
```
You can also run tests:
```bash
python -m pytest
```
## Contribute
Please feel free to contribute! You can find the source code [on GitHub](https://github.com/moinakmalkhan/Task-management)
## License
This project is licensed under the MIT license.
