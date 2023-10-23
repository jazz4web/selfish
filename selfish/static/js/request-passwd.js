function requestPasswd(token) {
  $.ajax({
    method: 'GET',
    url: '/api/request-passwd',
    headers: {
      'x-reg-token': token,
      'x-auth-token': window.localStorage.getItem('token')
    },
    success: function(data) {
      if (data.cu) {
        let html = Mustache.render($('#ealertt').html(), data);
        let interval = setInterval(function() {
          if ($('#main-container').length) {
            $('#main-container').append(html);
            slidePage('#ealert');
            clearInterval(interval);
          }
        }, 10);
      } else {
        if (!data.aid) {
          let html = Mustache.render($('#ealertt').html(), data);
          let interval = setInterval(function() {
            if ($('#main-container').length) {
              $('#main-container').append(html);
              slidePage('#ealert');
              clearInterval(interval);
            }
          }, 10);
        } else {
          let html = Mustache.render($('#crpt').html(), data);
          let interval = setInterval(function() {
            if ($('#main-container').length) {
              $('#main-container').append(html);
              slidePage('#crpf');
              clearInterval(interval);
            }
          }, 10);
        }
      }
    },
    dataType: 'json'
  });
}
