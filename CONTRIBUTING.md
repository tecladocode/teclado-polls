# Contributing guidelines

## Structure of the application

_Teclado polls_ is a small Flask web application. It uses PostgreSQL as a database.

In `app.py` we have the Python code: each of the endpoints that a user might access during their interactions with the application.

Each endpoint receives or returns some data.

When returning data for the user to see, often we're returning rendered HTML. Rendered HTML is calculated from Jinja2 code, which allows us to easily embed variables and repeat blocks before sending it to the user.

The templates are in `templates/`.

Some CSS and assets are in `static/`.

## Tests

At the moment there are no tests.

## Design

The design for the application can be found here, as a constant work-in-progress: [https://www.figma.com/file/JjeRWLO00URnE2zuxW6nO8/Teclado-Polls](https://www.figma.com/file/JjeRWLO00URnE2zuxW6nO8/Teclado-Polls)

## How to submit changes

Before submitting a change, have it agreed with the maintainers. You can do this by creating an Issue or commenting on an existing Issue. Doing this makes sure that you're the person working on the Issue, and that multiple people aren't working on the same issue at the same time.

Then the practicalities of submitting changes:

1. First, fork the repository.

2. Then clone it into your computer.

3. Make the changes there freely.

4. Then, push your changes to your fork.

5. Finally, submit a Pull Request from your fork into this repository.

When creating a Pull Request make sure to fill in the template and explain everything you've done. If your Pull Request is in response to an issue, put that in your Pull Request too!

## How to raise issues

To raise an issue, navigate to the Issues section and create one there. Fill in the template carefully. Provide screenshots if required to explain the problem.

If you'd like to add a feature to the application, providing a rough mockup of how you intend it to work is always a good idea.

If you'd like to modify the code structure, explaining why you think it would be better than what it is at the moment is always appreciated!