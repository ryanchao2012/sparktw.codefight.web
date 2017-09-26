// Empty JS for your own code to be here

function zero_padding(n, width, z) {
    z = z || '0';
    n = n + '';
    return n.length >= width ? n : new Array(width - n.length + 1).join(z) + n;
}

function format_elapsed(duration) {
	var hours = Math.floor(duration / 3600),
	minutes = Math.floor((duration - hours * 3600) / 60),
	seconds = Math.floor((duration - hours * 3600 - minutes * 60));
	return zero_padding(hours, 2) + ' hr ' + zero_padding(minutes, 2) + ' min ' + zero_padding(seconds, 2) + ' sec'
}

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
