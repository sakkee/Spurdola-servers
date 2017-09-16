<?php
/*One really messy file to handle registration, login and steamlogin*/
session_start();
if(isset($_SESSION['username'])) {
    header('Location: https://sakkee.org');
}
require("inc/database.php");

/*Returns a message that will tell the user what went wrong*/
$results = array(
    'error'=>true,
    'msg'=>"An error occured!"
);

if (isset($_POST["action"])) {
    if ($_POST["action"]=="toRegister") {
        if (isset($_POST["username"]) && isset($_POST["password1"]) && isset($_POST["password2"])) {
            $username = $_POST["username"];
            if (strlen($username)>2 && strlen($username)<13) {
                $pw = $_POST["password1"];
                if ($pw === $_POST["password2"]) {
                    if (strlen($pw) > 6 && strlen($pw) < 256) {
                        /*Checks if username is alphanumeric. We don't need to do the same to the password, because password goes through hashing
                        before entered to the SQL query*/
                        if (ctype_alnum($username)) {
                            $stmt = $db->prepare("SELECT * FROM www_accounts WHERE username=:username");
                            $stmt->execute(array(":username"=>$username));
                            $row = $stmt->fetch(PDO::FETCH_ASSOC);
                            if (!$row) {
                                $hashedPw = password_hash($pw,PASSWORD_BCRYPT);
                                $stmt = $db->prepare("INSERT INTO www_accounts (username, password) VALUES(:f1, :f2)");
                                $stmt->execute(array(":f1"=>ucfirst(strtolower($username)),":f2"=>$hashedPw));
                                $stmt = $db->prepare("SELECT * FROM www_accounts WHERE username=:username AND password=:password");
                                $stmt->execute(array(":username"=>$username, ":password"=>$hashedPw));
                                $row = $stmt->fetch(PDO::FETCH_ASSOC);
                                if ($row) {
                                    $_SESSION["username"] = $username;
                                    $_SESSION["id"] = $row["id"];
                                    $results["error"] = false;
                                    $results["msg"] = "You in da hood now!";
                                }
                                else {
                                    $results["msg"] = "Something very mysterious happened.";
                                }
                            }
                            else {
                                $results["msg"] = "The username you considered a special snowflake has been stolen. Pick another one.";
                            }
                        }
                        else {
                            $results["msg"] = "Username must consist of a-z, A-Z and 0-9 characters.";
                        }
                    }
                    else {
                        $results["msg"] = "Password must be between 8 and 255 characters long.";
                    }
                }
                else {
                    $results["msg"] = "Passwords aren't the same!";
                }
            }
            else {
                $results["msg"] = "Username must be between 3 and 12 characters long!";
            } 
        }
        else {
            $results["msg"] = "Please fill all the forms!";
        }
    }
    else if ($_POST["action"]=="toLogin") {
        if (isset($_POST["username"]) && isset($_POST["password"])) {
            if (ctype_alnum($_POST["username"])) {
                #TODO
                #$hashedPw = password_hash($_POST["password"],PASSWORD_BCRYPT);
                $stmt = $db->prepare("SELECT * FROM www_accounts WHERE username=:username");
                $stmt->execute(array(":username"=>$_POST["username"]));
                $row = $stmt->fetch(PDO::FETCH_ASSOC);
                if ($row) {
                    if (password_verify($_POST["password"],$row["password"])) {
                        $_SESSION["id"] = $row["id"];
                        $_SESSION["username"] = $row["username"];
                        $results["error"] = false;
                    }
                    else {
                        $results["msg"] = "Username or password wrong!";
                    }
                }
                else {
                    $results["msg"] = "Username or password wrong!";
                }
            }
            else {
                $results["msg"] = "Something strange with your input.";
            }
        }
        else {
            $results["msg"] = "Please fill all the forms!";
        }
    }
    echo json_encode($results);
}
else if (isset($_GET["logout"])) {
    session_destroy();
    header("Location: https://sakkee.org");
    
}
else {
    header("Location: https://sakkee.org");
}
  
?>