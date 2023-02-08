from flask import (
    Flask, redirect, render_template, request, session, url_for, flash
)

from database import (
    is_username_taken, add_user, authenticate, get_user_from_database,
    add_message, get_all_messages, delete_all_messages, delete_all_users
)


APP = Flask(__name__)
APP.config['SECRET_KEY'] = 'super-secret-key'

@APP.route('/')
@APP.route('/home')
def home():
    return render_template('home.html')

@APP.route('/about')
def about():
    return render_template('about.html')

@APP.route('/logout')
def logout():
    """Remove the session from the browser."""
    try:
        session.pop('username')
    except KeyError:
        pass
    return redirect('/login')
    
@APP.route('/messages', methods=['GET', 'POST'])
def messages():
    if request.method == 'POST':
        # This request is adding a new message from a logged-in user
        text = request.form['text']
        username = request.form['username']
        add_message(username, text)

    # Regardless of whether the request was GET or POST, we render the page
    # with all messages.
    return render_template(
        'messages.html',
        messages=get_all_messages()    )

@APP.route('/login', methods=['POST', 'GET'])
def login():
    """Render the login page.

    As with the signup page, there are two ways to interact with the login
    page: either by loading the page the first time (GET) or sending the
    credentials for authentication (POST).

    """
    if request.method == 'GET':
        # show the user the login page
        return render_template("login.html", session=session)
    else:
        # the user is trying to log in
        username = request.form['username']
        password = request.form['password']
        if authenticate(username, password):
            # save user to session and redirect to their Profile
            session['username'] = username
            return redirect('/profile')
        # failed login, redirect to login page
        flash("Wrong username or password. Try again.")
        return redirect(url_for('login'))

@APP.route('/signup', methods=['POST', 'GET'])
def signup():
    """Render the signup page.

    There are two ways to interact with the signup page: with a GET request or
    a POST request. A GET request just loads the signup page for the user to
    fill out. But when the user submits the signup form, their info is sent
    to the same URL as a POST request. (Think of it like mail: a GET request
    is like asking someone to send you a letter so you can GET it from your
    mailbox, and a POST request is like sending a letter using POSTage.) This
    function needs to handle both cases.

    Args:
        message (str): a message to display on the signup page (for errors).

    """
    # We need to do different things depending on whether the request is GET
    # or POST, so we check to see which one it is before we go any further.
    if request.method == 'GET':
        # Show the user the login page
        return render_template("signup.html", session=session)
    else:
        # The user is sending their data to sign up. We can now read their
        # information from a dictionary contained within the request, in the
        # attribute `request.form`.
        name = request.form['name']
        username = request.form['username']
        password = request.form['password']
        age = request.form['age']
        # Check to see if their desired username is taken
        if is_username_taken(username):
            # We will now reload the page with a message
            flash("Username already taken; please choose a different one.")
            """`flash` stores this message exclusively for the next request,
            which we immediately initiate using `redirect`. When the template
            loads, it checks for the presence of any flashed messages, and
            displays them as errors if so. (See `signup.html` and the included
            template `errors.html`.)
            """
            return redirect(url_for('signup'))

        """Since the line above has a `return` statement, execution of the
        function ends here: if the username was taken, nothing below this line
        will run. This means we can now assume that the username is available.
        """
        # Add user information to database
        add_user(name, username, password, age)

        # Save user to session and redirect to their Profile
        session['username'] = username
        return redirect(url_for('profile'))

@APP.route('/profile')
def profile():
    """Render the user's profile."""
    if 'username' in session:
        # if the user is logged in (a.k.a. in session)
        username = session['username']
        user = get_user_from_database(username)
        return render_template('profile.html', user=user)
    # user is not yet logged in
    message = "You must login to access your Profile."
    return render_template("login.html", message=message)


@APP.route('/resources')
def resources():
    return render_template('resources.html')

@APP.route('/pep')
def pep():
    return render_template('pep.html')


@APP.route('/delete')
def delete():
    # delete all messages
    delete_all_messages()
    delete_all_users()
    return redirect(url_for('home'))


if __name__ == "__main__":
    APP.run(port=8000, debug=True)