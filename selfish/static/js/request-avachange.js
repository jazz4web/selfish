function requestAvachange() {
  $(this).blur();
  $.ajax({
    method: 'GET',
    url: '/api/change-ava',
    headers: {
      'x-auth-token': window.localStorage.getItem('token')
    },
    success: function(data) {
      if (!data.cu) {
        let html = Mustache.render($('#ealertt').html(), data);
        slidePage('#ealert');
      } else {
        let html = Mustache.render($('#changeavat').html(), data);
        $('#main-container').append(html);
        if ($('.today-field').length) {
          let dt = luxon.DateTime.now();
          renderTF('.today-field', dt);
        }
        slidePage('#changeavaf');
      }
    },
    dataType: 'json'
  });
}
