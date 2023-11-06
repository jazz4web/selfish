function uploadPicture(event) {
  $('#ealert').remove();
  $('#upload-form-block').slideUp('slow', function() {
    $('#progress-block').slideDown('slow');
  });
  let file = $(this)[0].files[0];
  if (file.size <= 5 * 1024 * 1024) {
    let fd = new FormData($('#uploadform')[0]);
    fd.append('token', window.localStorage.getItem('token'));
    $.ajax({
      method: 'POST',
      url: '/api/pictures/' + event.data.suffix,
      processData: false,
      contentType: false,
      cache: false,
      data: fd,
      success: function(data) {
        if (data.done) {
          window.location.reload();
        } else {
          showError('#left-panel', data);
          $('#right-panel').addClass('next-block');
          $('#upload-form-block').slideDown('slow', function() {
            $('#progress-block').slideUp('slow');
          });
        }
      },
      dataType: 'json'
    });
  } else {
    let d = {message: 'Недопустимый размер файла.'};
    showError('#left-panel', d);
    $('#right-panel').addClass('next-block');
    $('#upload-form-block').slideDown('slow', function() {
      $('#progress-block').slideUp('slow');
    });
  }
}
