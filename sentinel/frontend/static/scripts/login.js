$(document).ready(function () {
    $('#loginForm').on('submit', function (event) {
        let loginForm = document.querySelector("#loginForm");
        let loginData = new FormData(loginForm);
        event.preventDefault();

        $.ajax({
            url: "/accounts/login/", // the endpoint
            type: "POST", // http method
            data: loginData, // data sent with the post request
            contentType: false,
            processData: false,
            // handle a successful response
            success: function (json) {
                if (json.accepted) {
                    window.location.replace("/dashboard/");
                } else {
                    document.querySelector("#login-alerts").innerHTML = '<div id="login-failed" class="alert alert-danger alert-dismissable fade in">\n' +
                        '                            <a href="#" class="close" data-dismiss="alert" aria-label="close">&times;</a>\n' +
                        '                            <strong>Login failed: </strong><span id="login-failed-text"></span>\n' +
                        '                        </div>';
                    document.querySelector('#login-failed-text').innerHTML = json.reason;
                    document.querySelector('#login-failed').classList.add('show')
                }
            },
                // handle a non-successful response
                error: function (xhr, errmsg, err) {
                    console.log(xhr.status + ": " + xhr.responseText); // provide a bit more info about the error to the console
                }
            });
    });

    $('#signupForm').on('submit', function (event) {
        let signupForm = document.querySelector("#signupForm");
        let signupData = new FormData(signupForm);
        event.preventDefault();
        if(signupData.get('password') !== signupData.get('checkPassword')) {
            document.querySelector("#signup-alerts").innerHTML = '<div id="signup-failed" class="alert alert-danger alert-dismissable fade in">\n' +
                        '                            <a href="#" class="close" data-dismiss="alert" aria-label="close">&times;</a>\n' +
                        '                            <strong>Sign up failed: </strong><span id="signup-failed-text"></span>\n' +
                        '                        </div>';
            document.querySelector('#signup-failed-text').innerHTML = "Passwords must match";
            document.querySelector('#signup-failed').classList.add('show')
            return false;
        }
        $.ajax({
            url: "register/", // the endpoint
            type: "POST", // http method
            data: signupData, // data sent with the post request
            contentType: false,
            processData: false,
            // handle a successful response
            success: function (json) {
                if (json.accepted) {
                    window.location.replace("/dashboard/");
                } else {
                    document.querySelector("#signup-alerts").innerHTML = '<div id="signup-failed" class="alert alert-danger alert-dismissable fade in">\n' +
                        '                            <a href="#" class="close" data-dismiss="alert" aria-label="close">&times;</a>\n' +
                        '                            <strong>Sign up failed: </strong><span id="signup-failed-text"></span>\n' +
                        '                        </div>';
                    document.querySelector('#signup-failed-text').innerHTML = json.reason;
                    document.querySelector('#signup-failed').classList.add('show');
                }
            },
                // handle a non-successful response
                error: function (xhr, errmsg, err) {
                    console.log(xhr.status + ": " + xhr.responseText); // provide a bit more info about the error to the console
                }
            });
    });
});