/*Passes registration inputs, shows output in case of an error*/
function register(username, password1, password2) {
    var request = $.ajax({
        url: "https://sakkee.org/registration.php",
        type: "POST",
        data: {
            "action": "toRegister",
            "username": username,
            "password1": password1,
            "password2": password2
        },
        dataType: "html",
        success: function(data) {
            var json = JSON.parse(data);
            
            if (json.error) {
                $("#error").innerHTML = json.msg;
                document.getElementById("error").innerHTML = json.msg;
            }
            else {
                window.location.href = "https://sakkee.org";
            }
        }
    });
}
/*Passes login inputs, shows output in case of an error*/
function login(username,password) {
    var request = $.ajax({
        url:"https://sakkee.org/registration.php",
        type: "POST",
        data: {
            "action": "toLogin",
            "username": username,
            "password": password
        },
        dataType: "html",
        success: function(data) {
            var json = JSON.parse(data);
            if (json.error) {
                document.getElementById("error").innerHTML = json.msg;
            }
            else {
                window.location.href = "https://sakkee.org";
            }
        }
        
    })
}

/*"Front page"*/
function indexForm() {
    var htmltext2 = '<p class="infotextBox">Nothing</p><input type="button" class="toProfile" value="My list">';
    document.getElementById("settingsBox").innerHTML = htmltext2;
    
}
/*"Profile page"*/
function profileForm() {
    var htmltext2 = '<p class="infotextBox">Go to main page </p><input type="button" class="toIndex" value="Main page">';
    document.getElementById("settingsBox").innerHTML = htmltext2;
    
}
/*Register window*/
function registerForm() {
    var htmltext = '<h4>Register</h4><div id="error"></div><input type="text" name="username" placeholder="Username"><br>';
    htmltext+= '<input type="password" name="password" placeholder="Password"/><br>';
    htmltext+= '<input type="password" name="password2" placeholder="Confirm password"/><br>';
    htmltext+= '<input type="button" id="registerButton" value="Register"><br><br>';
    htmltext+= 'Already have an account?<br><input type="button" class="toLogin" value="Login">';
    document.getElementById("loginBox").innerHTML = htmltext;
    $("#registerButton").click(function() {
        register($('input[name=username]').val(),$('input[name=password]').val(),$('input[name=password2]').val());
    })
}
/*User tries to use a member-only-function, such as mark as seen / follow, without being logged in*/
function goToLoginForm() {
    loginForm();
    $('html, body').animate({ scrollTop: 0 }, 'fast');
    $('#loginBox').effect("shake", {times:4}, 600);
}
/*Login window*/
function loginForm() {
    var htmltext = '<h4>Login</h4><div id="error"></div><input type="text" id="username" name="username" placeholder="Username">';
    htmltext+= '<br><input type="password" name="password" placeholder="Password"><br>';
    htmltext+= '<input type="button" id="loginButton" value="Login"><br><br>';
    htmltext+= 'Not yet a member? <br><input type="button" class="toRegister" value="Register!">';
    
    document.getElementById("loginBox").innerHTML = htmltext;
    $("#loginButton").click(function() {
        login($('input[name=username]').val(),$('input[name=password]').val());
    })
}

var loggedIn = 0;
var ready=1;
$(document).ready(function() {

    
    $(document).on('mousedown','.toLogin',function() {
        loginForm();
    })
    $(document).on('mousedown','.toRegister',function() {
        registerForm();
    })
    
    $(document).on('mousedown','.toLogout',function() {
        window.location.href = "https://sakkee.org/registration.php?logout";
    })
    $(document).on('mousedown','.toProfile',function() {
        profileForm();
    })
    $(document).on('mousedown','.toIndex',function() {
        indexForm();
        
    })

})