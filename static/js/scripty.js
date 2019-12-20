$(document).ready(function(){

    $(document).on('submit', '#login-form', function(e){
        e.preventDefault();

        var form = $(this).serialize();
        $.ajax({
            url: '/check_login',
            type: 'POST',
            data: form,
            success: function(res){
                if(res.toLowerCase()== "error"){
                    alert("Could not log in.");
                }else{
                    console.log("Logged in as", res);
                    window.location.href = "/";
                }
            }
        })
    });

        $(document).on('submit', '#register-form', function(e){
        e.preventDefault();

        var form = $(this).serialize();
        $.ajax({
            url: '/add_new_user',
            type: 'POST',
            data: form,
            success: function(res){
                if(res.toLowerCase()== "error"){
                    alert("Could not create user.");
                }else if(res.toLowerCase() == "user exists"){
                    alert("Username already taken");
                }else{
                }
                    console.log("Logged in as", res);
                    window.location.href = "/";
                }
            }
        })
    });

});