function changeAva() {
  $('#ealert').remove();
  $('#changeavaf').removeClass('next-block');
  let file = $(this)[0].files[0];
  if (file.size <= 204800) {
    let fd = new FormData($('#ava-form')[0]);
    fd.append('token', window.localStorage.getItem('token'));
    $.ajax({
      method: 'POST',
      url: '/api/change-ava',
      processData: false,
      contentType: false,
      cache: false,
      data: fd,
      success: function(data) {
        if (data.done) {
          window.location.reload();
        } else {
          showError('#changeavaf', data);
        }
      },
      dataType: 'json'
    })
  } else {
    let d = {message: 'Недопустимый размер файла.'};
    showError('#changeavaf', d);
  }
}
