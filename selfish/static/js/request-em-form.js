function requestEmF() {
  $(this).blur();
  $.ajax({
    method: 'GET',
    url: '/api/request-email-change',
    headers: {
      'x-auth-token': window.localStorage.getItem('token')
    },
    success: function(data) {
      if (!data.cu) {
        let html = Mustache.render($('#ealertt').html(), data);
        $('#main-container').append(html);
        slidePage('#ealert');
      } else {
        let html = Mustache.render($('#changeemt').html(), data);
        $('#main-container').append(html);
        if ($('.today-field').length) {
          let dt = luxon.DateTime.now();
          renderTF('.today-field', dt);
        }
        slidePage('#changeemf');
      }
    },
    dataType: 'json'
  });
}
