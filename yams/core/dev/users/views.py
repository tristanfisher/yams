from flask import Blueprint, jsonify, render_template, redirect, url_for, abort, flash
from yams_api.utils.logger import log
from .forms import EmailPasswordForm, EmailSignupForm
from .methods import User, YAMSAnonymousUser, confirm_token

core_users_bp = Blueprint("core_users", __name__, url_prefix="/users")


@core_users_bp.route("/", defaults={"id": "*"})
@core_users_bp.route("/<int:id>/")
def core_index(id):
    return render_template(
        "/core/dev/users.html",
        users=['tristan']
    )


@core_users_bp.route("/account")
def user_account():
    return render_template(
        "/core/dev/users.html",
        users=['todo: have this render an account management page']
    )

@core_users_bp.route("/account/login", methods=["GET", "POST"])
def user_account_login():

    form = EmailPasswordForm()
    if form.validate_on_submit():
        _user = User(
            email=form.email.data,
            password_from_web=form.password.data
        )
        # todo: call the API to see if this is correct
        return redirect(url_for('index'))

    return render_template(
        "/core/dev/users/login.html",
        form=form
    )


@core_users_bp.route("/account/create", methods=["GET", "POST"])
def user_account_create():

    form = EmailSignupForm()
    if form.validate_on_submit():

        # todo: call the API to try to create the account
        _user = User(
            first_name=form.first_name.data,
            email = form.email.data,
            password_from_web=form.password.data
        )
        try:
            _user.create_account()
        except ValueError as e:
            _error_message = str(e)


        return redirect(url_for('index'))

    return render_template(
        "/core/dev/users/create.html",
        form=form
    )



@core_users_bp.route("/account/activate")
def user_account_activate():

    # account_confirm_url

    return render_template(
        "/core/dev/users/activate.html",
        account_confirm_url=""
    )

@core_users_bp.route("/account/confirm/<token>")
def user_account_confirm(token):

    # fire off the token to the api for confirmation
    if not confirm_token(token):
        abort(404)

    flash("Thank you for confirming your account!")
    return redirect(url_for('index'))