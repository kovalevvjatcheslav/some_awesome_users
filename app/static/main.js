'use strict';

const TOKEN_PATTERN = new RegExp('token="?(?<token>[A-Za-z0-9=.]+)"?');

window.onload = async function() {
    const matching_value = document.cookie.match(TOKEN_PATTERN);
    if (matching_value !== null) {
        const token = matching_value.groups.token;
        remove_login_form();
        add_logout_button();
        if (get_user_permission() === "all") {
            add_create_user_button();
        }
        await build_users();
    }
}

function get_user_permission() {
    const matching_value = document.cookie.match(TOKEN_PATTERN);
    if (matching_value === null) {
        document.cookie = "token=;expires=Thu, 01 Jan 1970 00:00:01 GMT;";
        window.location.replace("/");
        return
    }
    const token = matching_value.groups.token;
    const payload = JSON.parse(atob(token.split(".")[1]));
    return payload.userType
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

function create_user_row(users_block, user, permission) {
    ["id", "name", "user_type", "created_at"].forEach(
        function(field_name) {
            const item = document.createElement("span");
            item.id = `${field_name}-${user.id}`
            item.innerHTML = user[field_name];
            users_block.appendChild(item);
        }
    );
    if (permission === "all") {
        const delete_button = document.createElement("button");
        delete_button.innerHTML = "delete";
        delete_button.id = `button-${user.id}`
        delete_button.addEventListener("click", remove_user);
        users_block.appendChild(delete_button);
    }
}

function delete_user_row(user_id) {
    ["id", "name", "user_type", "created_at", "button"].forEach(
        function(field_name) {
            const item = document.getElementById(`${field_name}-${user_id}`);
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
    const permission = get_user_permission();
    users.forEach(
        function(user) {
            create_user_row(users_block, user);
        }
    );

}

function add_logout_button() {
    let button = document.getElementById("logout-button");
    if (button === null) {
        button = document.createElement("button");
        button.id = "logout-button";
        button.innerHTML = "Logout";
        button.addEventListener("click", logout);
        document.getElementsByTagName("body")[0].appendChild(button);
    }
}

function add_create_user_button() {
    let button = document.getElementById("create-user-button");
    if (button === null) {
        button = document.createElement("button");
        button.id = "create-user-button";
        button.innerHTML = "Create user";
        button.addEventListener("click", show_create_form);
        document.getElementsByTagName("body")[0].appendChild(button);
    }
}

function show_create_form(event) {
    document.getElementById("modal-wrapper").style.display = "block";
}

function hide_create_form(event) {
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
    hide_create_form(event);
    if (resp.status === 409) {
        alert((await resp.json())["detail"]);
    }
    if (resp.ok) {
        const users_block = document.getElementById("users");
        const user = (await resp.json()).user;
        create_user_row(users_block, user);
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
    if (! resp.ok) {
        alert((await resp.json())["detail"]);
        return
    }
    delete_user_row(user_id);
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
        add_logout_button();
        if (get_user_permission() === "all") {
            add_create_user_button();
        }
        await build_users();
    }
    else {
        alert("Login or password is incorrect");
    }
}

async function logout(event) {
    const resp = await fetch(
        "/logout", {
            method: "POST",
            headers: {
                'Content-Type': 'application/json;charset=utf-8'
            },
        }
    );
    window.location.replace("/");
}