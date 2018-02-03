/* Project specific Javascript goes here. */

$body = $("body");

// Submit request on submit
$(document).ready(function() {
    var csrftoken = $("[name=csrfmiddlewaretoken]").val();
    function csrfSafeMethod(method) {
        // these HTTP methods do not require CSRF protection
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }

    $('#create-request').on('submit', function(event){
        event.preventDefault();
        console.log("form submitted!")  // sanity check
        create_post();
    });

    function create_post() {
//        var formData = new FormData($("#create-request").serializeArray());
        console.log("create post is working!") // sanity check
        var form = $('form')[0]
        var formData = new FormData(form);
        $.ajax({
            url : '/algos/', // the endpoint
            type : 'POST', // http method
            data : formData,
            cache: false,
            contentType: false,
            processData: false,
            beforeSend: function(xhr, settings) {
                $body.addClass("loading-pause");
                if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                    xhr.setRequestHeader("X-CSRFToken", csrftoken);
                }
            },
            // handle a successful response
            success : function(json) {
                if(json.success){
                    html = $("<div />").html(json.html).text()
                    $('#tabs-box-2').html(json.html)
                    $('#tabs-box-1').removeClass("in")
                    $('#tabs-box-1').removeClass("active")
                    $('#tabs-box-2').addClass("active")
                    $('#tabs-box-2').addClass("in")
                    $( "#nav-tab1" ).removeClass( "active" );
                    $( "#nav-tab2" ).addClass( "active" );
                    console.log("success"); // another sanity check
                }
                else{
                    $('#results').html('');
                    console.log("unsuccessful");
                    $('#results').html(json.html)
                }
            },
            complete: function(xhr, settings) {
                $body.removeClass("loading-pause");
            },
            // handle a non-successful response
            error : function(xhr,errmsg,err) {
                $('#results').html("<div class='alert-box alert radius' data-alert>Oops! We have encountered an error: "+errmsg+
                    " <a href='#' class='close'>&times;</a></div>"); // add the error to the dom
                console.log(xhr.status + ": " + xhr.responseText); // provide a bit more info about the error to the console
            }
        });
    };

    $('.request-content').on('click', ".list-item-sm", function(){
        if(!$(this).hasClass('active')){
            $(this).addClass('active')
        }
        else{
            $(this).removeClass('active')
        }
    });
});