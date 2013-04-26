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
    $(e.target.parentElement.parentElement).addClass('active');
});

$(function(){

    var $username = $("#box_perfil #user h2");

    var $letters = $username.text().length;

    if (($letters >= 1) && ($letters < 10)) {
        $username.css("font-size", "20px");
    }
    else if (($letters >= 10) && ($letters < 20)) {
        $username.css("font-size", "20px");
    }
    else if (($letters >= 20) && ($letters < 30)) {
        $username.css("font-size", "16px");
    }
    else if (($letters >= 30) && ($letters < 40)) {
        $username.css("font-size", "24px");
    }
    else {
        $username.css("font-size", "20px");
    }

});
