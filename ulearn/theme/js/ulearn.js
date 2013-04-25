customizedInput = false;

$('#addModal').on('shown', function () {
    if (!customizedInput) {
        customizedInput = true;
        $('[type=file]').customFileInput();
        }
});

$('#editModal').on('shown', function () {
    if (!customizedInput) {
        customizedInput = true;
        $('[type=file]').customFileInput();
        }
});

$('.portaltype-ulearn-community a[data-toggle="tab"]').on('show', function (e) {
    targetid = $(this).data('target');
    remote = $(targetid).data('remote');
    if (remote) {
        $(targetid).load(document.location.href + "/" + remote + '/ajax_folder_summary_view');
    }
    // console.log(targetid);
});

$('.portaltype-plone-site a[data-toggle="tab"]').on('show', function (e) {
    targetid = $(this).data('target');
    remote = $(targetid).data('remote');
    if (remote) {
        $(targetid).load(document.location.href + "/" + remote);
    }
    $('#menusup .bubble-container .active').removeClass('active');
    $(e.target.parentElement.parentElement).addClass('active')
});
