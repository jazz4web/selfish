function showIndex() {
  $.ajax({
    method: 'GET',
    url: '/api/index',
    success: function(data) {
      let dt = luxon.DateTime.now();
      data.year = dt.year;
      let html = Mustache.render($('#baset').html(), data);
      $('body').append(html);
      checkMC(800);
      if ($('.today-field').length) renderTF('.today-field', dt);
    },
    dataType: 'json'
  });
}

