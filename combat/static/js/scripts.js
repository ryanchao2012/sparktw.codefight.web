// Empty JS for your own code to be here


function flipPage(sel, uri, duration) {
    if (typeof(uri)==='undefined') uri = '/homepage/';
    if (typeof(duration)==='undefined') duration = 500;
    sel.fadeOut(duration, function() {
        $.get(uri)
        .success(function(data) {
            sel.html(data);
        });
        sel.fadeIn(duration);
    });

}
