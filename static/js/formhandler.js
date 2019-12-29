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

    $(document).on('submit', '#add_data_form', function(e){
        e.preventDefault();

        var form = $(this).serialize();
        $.ajax({
            url: '/add_hours',
            type: 'POST',
            data: form,
            success: function(res){
                if(res.toLowerCase()== "success"){
                    alert("Added successfully.");
                    $("#add_data_form")[0].reset();
                }else{
                    alert("Unknown error.");
                }
            }
        });

    });

    $(document).on('submit', '#register_form', function(e){
        e.preventDefault();

        var form = $(this).serialize();
        $.ajax({
            url: '/update_profile',
            type: 'POST',
            data: form,
            success: function(res){
                if(res.toLowerCase()== "success"){
                    alert("Added successfully.");
                    $("#register_form")[0].reset();
                }else{
                    alert("Unknown error.");
                }
            }
        })
    });

});
