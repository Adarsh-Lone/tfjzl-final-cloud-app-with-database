
**General Notes**

An `onlinecourse` app has already been provided in this repo upon which you will be adding a new assesement feature.

- If you want to develop the final project on Theia hosted by [IBM Developer Skills Network](https://labs.cognitiveclass.ai/), you will need to create the same project structure on Theia workspace and save it everytime you close the browser
- Or you could develop the final project locally by setting up your own Python runtime and IDE
- Hints for the final project are left on source code files
- You may choose any cloud platform for deployment (default is IBM Cloud Foundry)
- Depends on your deployment, you may choose any SQL database Django supported such as SQLite3, PostgreSQL, and MySQL (default is SQLite3)

**ER Diagram**
For your reference, we have prepared the ER diagram design for the new assesement feature.

![Onlinecourse ER Diagram](https://github.com/ibm-developer-skills-network/final-cloud-app-with-database/blob/master/static/media/course_images/onlinecourse_app_er.png)


## Assessment feature implementation notes

This working copy includes the Question, Choice, and Submission models; admin inlines and registrations; the plural `course_details_bootstrap.html` template required by the assignment; exam submission/result views; and URL routes.

### Run locally (Windows)

Use a Python version compatible with the pinned Django 3.1.3 dependency (Python 3.8–3.9 is a practical choice for this older starter). From the project folder:

```powershell
py -3.9 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python manage.py migrate --run-syncdb
python manage.py createsuperuser
python manage.py runserver
```

Open `http://127.0.0.1:8000/admin/` and add courses, lessons, questions, and choices. To test the learner flow, create a regular account, add an enrollment for that user and course (or use the Enroll button), and take the exam. Capture screenshots directly from your own running app; do not use mock or edited images as evidence.

### Before submission

Upload this corrected project to a GitHub repository you own or control, and submit the corresponding public file URLs. The starter repository and this working copy are references, not a substitute for your own submitted repository.
