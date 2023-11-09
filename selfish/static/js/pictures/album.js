$(function() {
  showAlbum(page, suffix);
  if (window.localStorage.getItem('token')) {
    $('body').on('click', '#show-rename-form', showRenameForm);
    $('body').on('click', '#show-state-form', showStateForm);
    $('body').on(
      'keyup blur', '#title-change',
      {min: 3, max: 100, block: '#rename-form'},
      markInputError);
    $('body').on('click', '#rename-album', {suffix: suffix}, renameAlbum);
    $('body').on('change', '#select-status', {suffix: suffix}, changeStatus);
    $('body').on('change', '#image', {suffix: suffix}, uploadPicture);
    $('body').on('click', '.album-header-panel', function() {
      if (!$(this).hasClass('clicked-item')) {
        let form = $('#upload-form-block');
        if (!form.is(':hidden')) form.slideUp('slow');
        $('.clicked-item').removeClass('clicked-item');
        $('.remove-button').each(function() { $(this).fadeOut('slow'); });
        $(this).addClass('clicked-item');
        let token = window.localStorage.getItem('token');
        let tee = token ? {'x-auth-token': token} : {};
        $.ajax({
          method: 'GET',
          url: '/api/picstat',
          headers: tee,
          data: {
            suffix: $(this).data().suffix
          },
          success: function(data) {
            if (data.picture) {
              let html = Mustache.render($('#picturet').html(), data);
              $('#right-panel').empty().append(html);
              formatDateTime($('.date-field'));
              let block_width = parseInt($('.album-statistic').width());
              let pic_width = parseInt($('.picture-body img').attr('width'));
              if (pic_width >= block_width) {
                let pic_height = parseInt($('.picture-body img')
                                          .attr('height'));
                let width = block_width - 4;
                let height = Math.round(pic_height / (pic_width / width));
                $('.picture-body img').attr({
                  "width": width, "height": height
                });
              }
              $('#copy-button').on('click', {cls: '.album-form'}, copyThis);
              $('#copy-button-b')
                .on('click', {cls: '.album-form-b'}, copyThis);
            } else {
              let html = Mustache.render($('#ealertt').html(), data);
              $('#main-container').append(html);
              showError('#left-panel', data);
              $('#right-panel').addClass('next-block');
            }
          },
          dataType: 'json'
        });
      }
    });
    $('body').on('click', '.copy-link', function() {
      $(this).blur();
      $('.remove-button').each(function() { $(this).fadeOut('slow'); });
      let ff = $('.album-form');
      let sf = $('.album-form-b');
      if (ff.is(':hidden')) {
        ff.slideDown('slow');
        sf.slideUp('slow');
      } else {
        ff.slideUp('slow');
      }
    });
    $('body').on('click', '.copy-md-code', function() {
      $(this).blur();
      $('.remove-button').each(function() { $(this).fadeOut('slow'); });
      let sf = $('.album-form-b');
      let ff = $('.album-form');
      if (sf.is(':hidden')) {
        sf.slideDown('slow');
        ff.slideUp('slow');
      } else {
        sf.slideUp('slow');
      }
    });
    $('body').on('click', '#album-reload', reload);
    $('body')
    .on('click', '#show-statistic', {suffix: suffix}, function(event) {
      $(this).blur();
      let form = $('#upload-form-block');
      if (!form.is(':hidden')) form.slideUp('slow');
      if ($('.clicked-item').length) {
        $('.clicked-item').removeClass('clicked-item');
        $('.remove-button').each(function() {$(this).fadeOut('slow'); });
        showAlbumStat(event.data.suffix);
      }
    });
    $('body').on('click', '#go-home', function() {
      $(this).blur();
      window.location.assign('/pictures/');
    });
    $('body').on('click', '#upload-new', {suffix: suffix}, function(event) {
      $(this).blur();
      let upblock = $('#upload-form-block');
      if (!upblock.is(':hidden')) {
        upblock.slideUp('slow');
      } else {
        if ($('.clicked-item').length) {
          $('.clicked-item').removeClass('clicked-item');
          $('.remove-button').each(function() { $(this).fadeOut('slow'); });
          showAlbumStat(event.data.suffix);
        }
        upblock.slideDown('slow');
        scrollPanel($('.albums-options'));
      }
    });
    $('body').on('click', '.trash-button', function() {
      $(this).blur();
      let alb = $(this).parents('.album-tools-panel')
                       .siblings('.album-header-panel');
      if (alb.hasClass('clicked-item')) showHideButton(
        $(this), '.remove-button');
    });
    $('body').on('click', '.page-link', {suffix: suffix}, function(event) {
      event.preventDefault();
      window.location.assign(
        '/pictures/' + event.data.suffix + '?page=' + $(this).text().trim());
    });
    $('body')
    .on('click', '#next-link', {page: page, suffix: suffix}, function(event) {
      event.preventDefault();
      let p = parseInt(event.data.page.trim()) + 1;
      window.location.assign('/pictures/' + event.data.suffix + '?page=' + p);
    });
    $('body')
    .on('click', '#prev-link', {page: page, suffix: suffix}, function(event) {
      event.preventDefault();
      let p = parseInt(event.data.page.trim()) - 1;
      window.location.assign('/pictures/' + event.data.suffix + '?page=' + p);
    });
    $('body')
    .on('click', '#album-first-page', {suffix: suffix}, function(event) {
      $(this).blur();
      window.location.assign('/pictures/' + event.data.suffix);
    });
    $('body')
      .on('click', '.remove-button', {page: page, suffix: suffix}, removeThis);
  }
});
