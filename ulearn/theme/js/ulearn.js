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
