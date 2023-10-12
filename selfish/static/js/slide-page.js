function slidePage(eid) {
  let block = $(eid);
  block.siblings().each(function() {
    $(this).slideUp('slow', function() { $(this).remove(); });
  });
  block.slideDown('slow');
}
