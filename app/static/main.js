'use strict';

const TOKEN_PATTERN = new RegExp('token="(?<token>[A-Za-z0-9=.]+)"');

window.onload = async function() {
    const matching_value = document.cookie.match(TOKEN_PATTERN);
    if (matching_value !== null) {
        const token = matching_value.groups.token;
        remove_login_form();
        add_create_user_button();
        await build_users();
    }
}

function remove_login_form(){
    const form = document.getElementById("login-form");
    form.remove();
}

function create_users_block_headers(users_block) {
    ["User id", "User name", "User Type", "Created at", ""].forEach(
        function (title) {
            const item = document.createElement("span");
            item.innerHTML = title;
            users_block.appendChild(item);
        }
    );
}

function create_user_row(users_block, user) {
    for (const prop in user) {
        const item = document.createElement("span");
        item.id = `${prop}-${user.id}`
        item.innerHTML = user[prop];
        users_block.appendChild(item);
    }
    const delete_button = document.createElement("button");
    delete_button.innerHTML = "delete";
    delete_button.id = `button-${user.id}`
    delete_button.addEventListener("click", remove_user);
    users_block.appendChild(delete_button);
}

function delete_user_row(user_id) {
    ["id", "name", "user_type", "created_at", "button"].forEach(
        function(title) {
            const item = document.getElementById(`${title}-${user_id}`);
            item.remove();
        }
    );
}

async function build_users() {
    const resp = await fetch(
        "/users", {
            method: "GET",
            headers: {
                'Content-Type': 'application/json;charset=utf-8'
            }
        }
    );
    if (resp.status === 403) {
        document.cookie = "token=;expires=Thu, 01 Jan 1970 00:00:01 GMT;";
        window.location.replace("/");
        return
    }
    let users_block = document.getElementById("users");
    if (users_block === null) {
        users_block = document.createElement("div");
        users_block.id = "users";
        users_block.classList.add("grid-container");
        document.getElementsByTagName("body")[0].appendChild(users_block);
    }

    create_users_block_headers(users_block);

    const users = (await resp.json()).users;
    users.forEach(
        function(user) {
            create_user_row(users_block, user);

            console.log(user)
        }
    );

}

function add_create_user_button() {
    let button = document.getElementById("create-user-button");
    if (button === null) {
        button = document.createElement("button");
        button.id = "create-user-button";
        button.innerHTML = "Create user";
        button.addEventListener("click", show_add_form);
        document.getElementsByTagName("body")[0].appendChild(button);
    }
}

function show_add_form(event) {
    document.getElementById("modal-wrapper").style.display = "block";
}

function hide_add_form(event) {
    document.getElementById("modal-wrapper").style.display = "none";
}

async function create_user(form, event) {
    event.preventDefault();
    const name = form.elements["create-username-input"].value;
    const password = form.elements["create-password-input"].value;
    const user_type = form.elements["user-type"].value;
    const resp = await fetch(
        "/user", {
            method: "POST",
            headers: {
                'Content-Type': 'application/json;charset=utf-8'
            },
            body: JSON.stringify({"name": name, "password": password, "user_type": user_type})
        }
    );
    hide_add_form(event);
    if (resp.status === 409){
        alert("The user with the current name already exists");
    }
}

async function remove_user(event) {
    const user_id = event.target.id.split("-")[1];
    const resp = await fetch(
        `/user/${user_id}`, {
            method: "DELETE",
            headers: {
                'Content-Type': 'application/json;charset=utf-8'
            }
        }
    );
    delete_user_row(user_id);
    console.log(resp.status);
}

async function login(form, event) {
    event.preventDefault();
    const name = form.elements["username-input"].value;
    const password = form.elements["password-input"].value;
    const resp = await fetch(
        "/login", {
            method: "POST",
            headers: {
                'Content-Type': 'application/json;charset=utf-8'
            },
            body: JSON.stringify({"name": name, "password": password})
        }
    );
    if (resp.ok) {
        remove_login_form();
        add_create_user_button();
        await build_users();
    }
    else {
        alert("Login or password is incorrect");
    }
}