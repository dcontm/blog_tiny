// Получаем csrf token
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
var csrftoken = getCookie('csrftoken');

/*
The functions below will create a header with csrftoken
*/

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}
function sameOrigin(url) {
    // test that a given url is a same-origin URL
    // url could be relative or scheme relative or absolute
    var host = document.location.host; // host + port
    var protocol = document.location.protocol;
    var sr_origin = '//' + host;
    var origin = protocol + sr_origin;
    // Allow absolute or scheme relative URLs to same origin
    return (url == origin || url.slice(0, origin.length + 1) == origin + '/') ||
        (url == sr_origin || url.slice(0, sr_origin.length + 1) == sr_origin + '/') ||
        // or any other URL that isn't scheme relative or absolute i.e relative.
        !(/^(\/\/|http:|https:).*/.test(url));
}
// ======================================================================================================================
//like function
$(function() {
    $(document).on('click', '.likes', function() {
            var object_id = $(this).data('id')
            var action_type = $(this).data('type')

            $.ajax({
                url : '/'+action_type+'/'+ object_id +'/like/',
                context: $(this),
                type : 'POST',


                success : function(data) {
                    if (data) {
                        $(this).siblings('.countlikes').text(data.likes);
                        $(this).parents('.likesystem').find('.countdislikes').text(data.dislikes);
                    }
                    console.log(data);
                },

                error : function(xhr,errmsg,err) {
                    console.log(xhr.status+': '+xhr.responseText);
                    $('#exampleModalCenter').modal('show');
                },
            });
    });
    
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type) && sameOrigin(settings.url)) {
                // Send the token to same-origin, relative URLs only.
                // Send the token only if the method warrants CSRF protection
                // Using the CSRFToken value acquired earlier
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });

});



// ======================================================================================================================
//dislike function
$(function() {
    $(document).on('click', '.dislikes', function() {
            var object_id = $(this).data('id')
            var action_type = $(this).data('type')

            $.ajax({
                url : '/'+action_type+'/'+ object_id +'/dislike/',
                context: $(this),
                type : 'POST',

                success : function(data) {
                    if (data) {
                        $(this).parents('.likesystem').find('.countlikes').text(data.likes);
                        $(this).siblings('.countdislikes').text(data.dislikes);
                    }
                    console.log(data);
                },

                error : function(xhr,errmsg,err) {
                    console.log(xhr.status+': '+xhr.responseText);
                    $('#exampleModalCenter').modal('show');
                },
            });
    });

    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type) && sameOrigin(settings.url)) {
                // Send the token to same-origin, relative URLs only.
                // Send the token only if the method warrants CSRF protection
                // Using the CSRFToken value acquired earlier
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });

});


// ======================================================================================================================
// create comment function
$(function() {
    $(document).on('click', '#addcomment', function(event) {
            event.preventDefault();
            var object_id = $('#addcomment').data('id')
            var type = $('#addcomment').data('type')

            $.ajax({
                url : '/'+type+'/'+object_id+'/comments/',
                type : 'POST',
                data : { message: $('#id_message').val() },

                success : function(data) {
                    if (data) {
                        var comment = $.parseHTML(data.new_comment);
                        $('#comments_block').prepend(comment);
                        $('#comments_count').text(data.comments_count);
                        $('#comments_count_str').text(data.comments_count);
                        $('#id_message').val('');
                    }
                    console.log(data.comments_count);
                },

                error : function(xhr,errmsg,err) {
                    console.log(xhr.status+': '+xhr.responseText);
                    var JsonResponseText = JSON.parse(xhr.responseText);
                    var spam = JsonResponseText.spam ;
                    if (spam === true){
                        $('#spamModal').modal('show');
                    }
                },
            });
    });

    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type) && sameOrigin(settings.url)) {
                // Send the token to same-origin, relative URLs only.
                // Send the token only if the method warrants CSRF protection
                // Using the CSRFToken value acquired earlier
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });

});


// ======================================================================================================================
// delete comment function
$(function() {
    $(document).on('click', '.deletecomment', function(event) {

            event.preventDefault();
            var comment_id = $(this).data('id')

            $.ajax({
                url : '/comment/'+ comment_id+'/delete/',
                type : 'POST',
                context : $(this),


                success : function(data) {
                    if (data) {
                        $(this).parents('.comments')[0].remove()
                        $('#comments_count').text(data.comments_count);
                        $('#comments_count_str').text(data.comments_count);
                        $('#id_message').val('');
                    }
                    console.log(data);
                },

                error : function(xhr,errmsg,err) {
                    console.log(xhr.status+': '+xhr.responseText);
                },
            });
    });

    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type) && sameOrigin(settings.url)) {
                // Send the token to same-origin, relative URLs only.
                // Send the token only if the method warrants CSRF protection
                // Using the CSRFToken value acquired earlier
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });

});


// ======================================================================================================================
// preview update function
$(function() {
    $(document).on('click', '.updatecomment', function(event){
        event.preventDefault();
        var comment_id = $(this).data('id');
        var post_id = $('#addcommentform').data('id');
        $('#closeaddcomment').show()
        var message = $('.commentmessage[data-id='+comment_id+']');
        $('#id_message').val($(message).text()).focus();
        $('#addcomment').replaceWith('<button type="submit" class="btn-submit"  id="updatecomment" data-comment='+comment_id+' data-id='+post_id+'>Сохранить</button>');
        $('#answercomment').replaceWith('<button type="submit" class="btn-submit"  id="updatecomment" data-comment='+comment_id+' data-id='+post_id+'>Сохранить</button>');
        
    })

});
// ======================================================================================================================
// update function
$(function() {
    $(document).on('click', '#updatecomment', function(event) {
            event.preventDefault();
            var comment_id = $(this).data('comment')
            var post_id = $('#addcommentform').data('id');


            $.ajax({
                url : '/comment/'+ comment_id+'/update/',
                type : 'POST',
                data : { message: $('#id_message').val() },
                context : comment_id, post_id,

                success : function(data) {
                    if (data) {
                        var comment = $('.comments[data-id='+comment_id+']');
                        var commentcreated = $('.commentcreated[data-id='+comment_id+']');
                        var message = $('.commentmessage[data-id='+comment_id+']');
                        $(message).text(data.message).focus();
                        $(commentcreated).text(data.created+' | изменено');
                        $('#updatecomment').replaceWith("<button type='submit' class='btn-submit' id='addcomment' data-id="+post_id+">Отправить</button>");
                        $('#closeaddcomment').hide();
                        $("html,body").animate({scrollTop: $(comment).offset().top-150}, 500);
                        $('#id_message').val('');
                    }
                    console.log(data);
                },

                error : function(xhr,errmsg,err) 
                {
                    console.log(xhr.status+': '+xhr.responseText);
                },
            });
    });

    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type) && sameOrigin(settings.url)) {
                // Send the token to same-origin, relative URLs only.
                // Send the token only if the method warrants CSRF protection
                // Using the CSRFToken value acquired earlier
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });

});
// ======================================================================================================================
// preview answer function
$(function() {
    $(document).on('click', '.answercomment', function(event){
        event.preventDefault();
        var comment_id = $(this).data('id');
        var post_id = $('#addcommentform').data('id');
        var user_name = $('.commentauthor[data-id='+comment_id+']').text();
        $('#closeaddcomment').show()
        $('#id_message').val(user_name+', ').focus();
        $('#addcomment').replaceWith('<button type="submit" class="btn-submit"  id="answercomment" data-comment='+comment_id+' data-id='+post_id+'>Ответить</button>');
        $('#updatecomment').replaceWith('<button type="submit" class="btn-submit"  id="answercomment" data-comment='+comment_id+' data-id='+post_id+'>Ответить</button>');
        
    })

});
// ======================================================================================================================
// click close
$(function() {
    $(document).on('click', '#closeaddcomment', function(event){
        event.preventDefault();
        var post_id = $('#addcommentform').data('id');
        $('#id_message').val('').focus();
        $('#updatecomment').replaceWith("<button type='submit' class='btn-submit' id='addcomment' data-id="+post_id+">Отправить</button>");
        $('#answercomment').replaceWith("<button type='submit' class='btn-submit' id='addcomment' data-id="+post_id+">Отправить</button>");
        $('#closeaddcomment').hide();
        
    })

});

// ======================================================================================================================
// create answer
$(function() {
    $(document).on('click', '#answercomment', function(event) {
            event.preventDefault();
            var comment_id = $(this).data('comment')
            var post_id = $('#answercomment').data('id');


            $.ajax({
                url : '/comment/'+ comment_id+'/answer/',
                type : 'POST',
                data : { message: $('#id_message').val() },
                context : comment_id,

                success : function(data) {
                    var answer = $.parseHTML(data.new_answer);
                    var comment = $('.comments[data-id='+comment_id+']');
                    if (data.status === 1){
                        $(comment).parent().append(answer);
                    }
                    else if (data.status ===0){
                        $(comment).find('.answers_block').append(answer);
                    }
                    $('#answercomment').replaceWith("<button type='submit' class='btn-submit' id='addcomment' data-id="+post_id+">Отправить</button>");
                    $('#comments_count').text(data.comments_count);
                    $('#comments_count_str').text(data.comments_count);
                    $('#closeaddcomment').hide();
                    $("html,body").animate({scrollTop: $(comment).offset().top-150}, 500);
                    console.log(data.status);
                },

                error : function(xhr,errmsg,err) 
                {
                    console.log(xhr.status+': '+xhr.responseText);
                    var JsonResponseText = JSON.parse(xhr.responseText);
                    var spam = JsonResponseText.spam ;
                    if (spam === true){
                        $('#spamModal').modal('show');
                    }
                },
            });
    });

    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type) && sameOrigin(settings.url)) {
                // Send the token to same-origin, relative URLs only.
                // Send the token only if the method warrants CSRF protection
                // Using the CSRFToken value acquired earlier
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });

});


// ======================================================================================================================
// function update avatar
$(function() {
    $(document).on('click', '#update_avatar', function(event) {
            event.preventDefault();

            $.ajax({
                url : '/update_avatar/',
                type : 'POST',

                success : function(data) {
                    if (data) {
                        $('#avatar').attr("src",data.avatar_url);
                    }
                    console.log(data);
                },

                error : function(xhr,errmsg,err) {
                    console.log(xhr.status+': '+xhr.responseText);
                },
            });
    });

    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type) && sameOrigin(settings.url)) {
                // Send the token to same-origin, relative URLs only.
                // Send the token only if the method warrants CSRF protection
                // Using the CSRFToken value acquired earlier
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });

});
//=============================================================================================================

//subs function
$(function() {
    $('.subscribe').change(function(event) {
            var type_subs =$(this).data('subs')

            $.ajax({
                url : '/profile/settings/'+ type_subs +'/',
                type : 'POST',

                success : function(data) {
                    console.log(data);
                },

                error : function(xhr,errmsg,err) {
                    console.log(xhr.status+': '+xhr.responseText);
                    $('#exampleModalCenter').modal('show');
                },
            });
    });
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type) && sameOrigin(settings.url)) {
                // Send the token to same-origin, relative URLs only.
                // Send the token only if the method warrants CSRF protection
                // Using the CSRFToken value acquired earlier
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });
});

// ======================================================================================================================
//vote function
$(function() {
    $(document).on('click', '.vote', function() {
            var variable_id = $(this).data('id');
            var news_id = $(this).data('news-id');

            $.ajax({
                url : '/variable/'+ variable_id +'/',
                context: $(this),news_id,
                type : 'POST',


                success : function(data) {
                    if (data) {
                        //var variables = $('.vote[data-news-id='+news_id+']');
                        var votes = data.votes
                        votes.forEach(function(item, i, votes){
                            variable =  $('.vote[data-id='+item[0]+']');
                            $(variable).find('.progress-bar').width(item[2]+'%');
                            $(variable).find('.progress-bar').attr('aria-valuenow',item[2]);
                            $(variable).find('.vote-label').text(item[2]+'%');
                            });
                        $('.votes_count[data-news-id='+news_id+']').text('Проголосовало '+data.total_votes);

                    }
                    console.log('success');
                },

                error : function(xhr,errmsg,err) {
                    console.log(xhr.status+': '+xhr.responseText);
                    $('#votesErrorModal').modal('show');
                },
            });
    });
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type) && sameOrigin(settings.url)) {
                // Send the token to same-origin, relative URLs only.
                // Send the token only if the method warrants CSRF protection
                // Using the CSRFToken value acquired earlier
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });
});


// ======================================================================================================================