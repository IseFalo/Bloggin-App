console.log("new")
document.getElementById('profile-image-input').addEventListener('change', function(event){
    var input = event.target
    var reader = new FileReader();

    reader.onload = function(){
        var dataURL=reader.result;
        var previewImage = document.getElementById('settings-profile-img');
        previewImage.src = dataURL;

    };
    reader.readAsDataURL(input.files[0]);
})