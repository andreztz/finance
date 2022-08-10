var main = function() 
{
    function testPasswords(password, confirmPassword) 
    {
        return password === confirmPassword
    }

    function checkPasswordComplexity(password)
    {
        let pattern = new RegExp("^(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])(?=.*[!@#\$%\^&\*])(?=.{8,})")
        return pattern.test(password)
    }

    function checkUsername(username)
    {
        let pattern = new RegExp("^(?=.*)[A-Za-z_0-9]{4,10}$")
        return pattern.test(username) 
    }

    let $ = function (elem) {
        return document.querySelector(elem)
    }
    let message = $("#message")

    let username = $("#username")
    let usernameMessage = $("#usernameMessage")

    let password = $("#password")
    let passwordMessage = $("#passwordMessage")

    let confirmation = $("#confirmation")
    let confirmationMessage = $("#confirmationMessage")

    let registerForm = $("#registerForm")

    let passwordsMatch = false
    let passwordIsComplex = false
    let usernameOK = false

    username.addEventListener("keyup", (event) => {
        if (checkUsername(event.target.value))
        {
            usernameMessage.innerHTML = ""
            usernameOK = true
        }
        else
        {
            usernameMessage.innerHTML = "Username must contains letters, numbers and underscores."
            usernameOK = false
        }
    })

    password.addEventListener("keyup", (event) => {
        if (checkPasswordComplexity(event.target.value)) 
        {
            passwordMessage.innerHTML = ""
            passwordIsComplex = true
        }
        else 
        {
            passwordMessage.innerHTML = "The password is not complex enough!"
            passwordIsComplex = false
        }
    })

    confirmation.addEventListener("keyup", (event) => {
        // debugger
        if (testPasswords(password.value, confirmation.value))
        {
            confirmationMessage.innerHTML = ""
            passwordsMatch = true
        } 
        else 
        {
            confirmationMessage.innerHTML = "Passwords not matching!"
            passwordsMatch = false
        }
    })

    registerForm.addEventListener("submit", (event) => {
        event.preventDefault();

        if (usernameOK && passwordIsComplex && passwordsMatch)
        {
            // debugger
            message.innerHTML = ""
            event.target.submit()
        }
        else
        {
            message.innerHTML = "Formulário inválido, confira seus dados."
        }
    })
}   

document.addEventListener(
    'DOMContentLoaded',
    main
)
