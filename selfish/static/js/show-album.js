function showAlbum(page, suffix) {
  let token = window.localStorage.getItem('token');
  let tee = token ? {'x-auth-token': token} : {};
  $.ajax({
    method: 'GET',
    url: '/api/pictures/' + suffix,
    data: {
      page: page
    },
    headers: tee,
    success: function(data) {
      if (token) {
        if (!data.cu || data.cu.brkey != checkBrowser()) {
          window.localStorage.removeItem('token');
          window.location.reload();
        }
      }
      console.log(data);
      let dt = luxon.DateTime.now();
      data.year = dt.year;
      let html = Mustache.render($('#baset').html(), data);
      $('body').append(html);
      checkMC(1152);
      $('body').on('click', '.close-top-flashed', closeTopFlashed);
      if (data.message) {
        let html = Mustache.render($('#ealertt').html(), data);
        $('#main-container').append(html);
        slidePage('#ealert');
      } else {
        let title = $('title').text().trim() + ' ' + data.album.parsed36;
        $('title').text(title);
        let html = Mustache.render($('#albumt').html(), data);
        $('#main-container').append(html);
        let ast = Mustache.render($('#astatt').html(), data);
        $('#right-panel').append(ast);
        if ($('.today-field').length) renderTF('.today-field', dt);
        formatDateTime($('.date-field'));
        $('#progress-block').hide();
        let s = $('#select-status option');
        for (let n = 0; n < s.length; n++) {
          if (s[n].value == data.album.state) {
            $(s[n]).attr('selected', 'selected');
          }
        }
      }
    },
    dataType: 'json'
  });
}
