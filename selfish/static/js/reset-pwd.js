function resetPwd() {
  $(this).blur();
  let tee = {
    address: $('#rsaddress').val(),
    passwd: $('#rspassword').val(),
    confirma: $('#rsconfirm').val(),
    aid: $(this).data().aid
  };
  if (tee.address && tee.passwd && tee.confirma && tee.aid) {
    $.ajax({
      method: 'POST',
      url: '/api/reset-passwd',
      data: tee,
      success: function(data) {
        if (data.done) {
          $('.navbar-brand')[0].click();
        } else {
          showError('#rspf', data);
        }
      },
      dataType: 'json'
    });
  }
}
