$(document).ready(function(){

    $(document).on('submit', '#login_form', function(e){
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

});