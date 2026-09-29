var canvas = document.getElementById('canvas')
var ctx = canvas.getContext('2d')
var csrfToken = document.getElementById('capture').dataset.csrfToken
var video = document.getElementById('preview')
var button = document.getElementById('capture-button')
var upload = document.getElementById('upload')
var uploadPreview = document.getElementById('upload-preview')
var errorBox = document.getElementById('preview-error')
var webcamReady = false
var fileImage = false


function send(pixels, overlays) {
    button.disabled = true
    errorBox.textContent = "Processing..."

    fetch('/images?overlay=' + encodeURIComponent(overlays.join(',')), {
        method: 'POST',
        headers: {
            'Content-Type': 'application/octet-stream',
            'X-CSRF-Token': csrfToken
        },
        body: pixels
    }).then(function (res) {
        if (res.status === 201) {
            location.reload()
            return
        } else if (res.status === 403) {
            errorBox.textContent = "Session expired, please reload the page."
            updateButton()
            return
        }
        return res.text().then(function (text) {
            errorBox.textContent = text
            updateButton()
        })
    }).catch(function () {
        errorBox.textContent = "Network error, please try again."
        updateButton()
    })

}


function selectedOverlays() {
    var checked = document.querySelectorAll('input[name="overlay"]:checked')
    var values = []
    for (var i = 0; i < checked.length; i++) {
        values.push(checked[i].value)
    }
    return values
}


function updateButton() {
    button.disabled = !(webcamReady || fileImage)
}


navigator.mediaDevices.getUserMedia({ video: { width: 640, height: 480 } })
    .then(function (stream) { video.srcObject = stream })
    .catch(function () {
        video.hidden = true
        errorBox.textContent = "Webcam unavailable. You can still upload a picture below."
    })

var radios = document.querySelectorAll('input[name="overlay"]')
for (var i = 0; i < radios.length; i++) {
    radios[i].addEventListener('change', updateButton)
}

video.addEventListener('playing', function () {
    webcamReady = true
    updateButton()
})

button.addEventListener('click', function () {
    var source = fileImage ? uploadPreview : video
    ctx.drawImage(source, 0, 0, 640, 480)
    var pixels = ctx.getImageData(0, 0, 640, 480).data
    send(pixels, selectedOverlays())
})

upload.addEventListener('change', function () {
    var file = upload.files[0]
    if (!file) return
    uploadPreview.src = URL.createObjectURL(file)
})

uploadPreview.addEventListener('load', function() {
    uploadPreview.hidden = false
    video.hidden = true
    fileImage = true
    errorBox.textContent = ""
    updateButton()
})

uploadPreview.addEventListener('error', function() {
    uploadPreview.hidden = true
    video.hidden = !webcamReady
    errorBox.textContent = "This file is not a valid image."
    fileImage = false
    updateButton()
})