$(function() {
  console.log('yep!');
  checkMC(800);
  let dt = luxon.DateTime.now();
  if ($('.today-field').length) renderTF('.today-field', dt);
});
