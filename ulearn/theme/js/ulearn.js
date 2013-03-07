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

$('a[data-toggle="tab"]').on('show', function (e) {
    targetid = $(this).data('target');
    $(targetid).load();
    console.log(targetid);
})
