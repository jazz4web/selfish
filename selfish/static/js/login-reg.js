function loginReg() {
  $(this).blur();
  window.location.hash = '#get-password';
  $('#reg').trigger('click');
}
