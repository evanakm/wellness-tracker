$(document).ready(function(){

    $(document).on('submit', '#login-form', function(e){
        e.preventDefault();

        var form = $(this).serialize();
        $.ajax({
            url: '/check_login',
            type: 'POST',
            data: form,
            success: function(res){
                if(res== "error"){
                    alert("Could not log in.");
                }else{
                    console.log("Logged in as", res);
                    window.location.href = "/";
                }
            }
        })
    });
});