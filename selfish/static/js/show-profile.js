function showProfile() {
  let token = window.localStorage.getItem('token');
  let tee = token ? {'x-auth-token': token} : {};
  $.ajax({
    method: 'GET',
    url: '/api/profile',
    headers: tee,
    data: {
      username: username
    },
    success: function(data) {
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
      if (data.message) {
        let html = Mustache.render($('#ealertt').html(), data);
        $('#main-container').append(html);
        slidePage('#ealert');
      } else {
        let html = Mustache.render($('#profilet').html(), data);
        $('#main-container').append(html);
        formatDateTime($('#profile .date-field'));
        renderLastSeen($('#profile .last-seen'));
        if ($('#permissions-block').length) {
          $('#perms-submit').on(
              'click', {username: data.user.username,
                        perms: data.perms}, function(event) {
            event.preventDefault();
            $(this).blur();
            let tee = {
              auth: window.localStorage.getItem('token'),
              user: event.data.username};
            for (let m = 0; m < event.data.perms.length; m++) {
              let inp = $('#' + event.data.perms[m]);
              if (inp.length) {
                tee[event.data.perms[m]] = inp.is(':checked') ? 1 : 0;
              }
            }
            $.ajax({
              method: 'POST',
              url: '/api/profile',
              data: tee,
              success: function(data) {
                if (data.done) {
                  window.location.reload();
                } else {
                  $('.top-flashed-block').slideUp('slow', function() {
                    $('.top-flashed-block').remove();
                  });
                  showError('#profile', data);
                }
              },
              dataType: 'json'
            });
          });
          let blocker = $('#nologin');
          if (blocker.length) {
            blocker.on('change', function() {
              if ($(this).is(':checked')) {
                uncheckBox('#read');
                uncheckBox('#follow');
                uncheckBox('#like');
                uncheckBox('#pm');
                uncheckBox('#comment');
                uncheckBox('#alias');
                uncheckBox('#art');
                uncheckBox('#block');
                uncheckBox('#churole');
                uncheckBox('#picture');
                uncheckBox('#announce');
                uncheckBox('#administer');

              } else {
                checkBox('#read');
              }
            });
          }
          let reader = $('#read');
          if (reader.length) {
            reader.on('change', function() {
              if ($(this).is(':checked')) {
                uncheckBox('#nologin');
              } else {
                checkBox('#nologin');
                uncheckBox('#follow');
                uncheckBox('#like');
                uncheckBox('#pm');
                uncheckBox('#comment');
                uncheckBox('#alias');
                uncheckBox('#art');
                uncheckBox('#block');
                uncheckBox('#churole');
                uncheckBox('#picture');
                uncheckBox('#announce');
                uncheckBox('#administer');
              }
            });
          }
          let admin = $('#administer');
          if (admin.length) {
            admin.on('change', function() {
              if ($(this).is(':checked')) {
                uncheckBox('#nologin');
                checkBox('#read');
                checkBox('#follow');
                checkBox('#like');
                checkBox('#pm');
                checkBox('#comment');
                checkBox('#alias');
                checkBox('#art');
                checkBox('#block');
                checkBox('#churole');
                checkBox('#picture');
                checkBox('#announce');
              }
            });
          }
          checkAverage('#follow');
          checkAverage('#like');
          checkAverage('#pm');
          checkAverage('#comment');
          checkAverage('#alias');
          checkAverage('#art');
          checkAverage('#block');
          checkAverage('#churole');
          checkAverage('#picture');
          checkAverage('#announce');
        }
      }
    },
    dataType: 'json'
  });
}
