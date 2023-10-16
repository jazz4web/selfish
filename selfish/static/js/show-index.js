function showIndex() {
  let token = window.localStorage.getItem('token');
  let tee = {};
  if (token) {
    tee['x-auth-token'] = token;
  }
  $.ajax({
    method: 'GET',
    url: '/api/index',
    headers: tee,
    success: function(data) {
      console.log(data);
      if (token) {
        if (!data.cu || data.cu.brkey != checkBrowser()) {
          window.localStorage.removeItem('token');
          window.location.reload();
        }
      }
      let dt = luxon.DateTime.now();
      data.year = dt.year;
      let html = Mustache.render($('#baset').html(), data);
      $('body').append(html);
      checkMC(800);
      $('body').on('click', '.close-top-flashed', closeTopFlashed);
      let content = Mustache.render($('#indext').html(), data);
      $('#main-container').append(content);
      if ($('.today-field').length) renderTF('.today-field', dt);
    },
    dataType: 'json'
  });
}

