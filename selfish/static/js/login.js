function login() {
  $.ajax({
    method: 'GET',
    url: '/api/captcha',
    success: function(data) {
      let form = Mustache.render($('#logint').html(), data);
      let interval = setInterval(function() {
        if ($('#main-container').length) {
          $('#main-container').append(form);
          slidePage('#loginf');
          clearInterval(interval);
        }
      }, 10);
    },
    dataType: 'json'
  });
  let col = $(this).parents('.navbar-collapse');
  if (col.hasClass('in')) col.removeClass('in');
}
